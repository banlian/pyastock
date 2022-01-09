import time

import pandas as pd
import os
from pytdx.reader import TdxDailyBarReader

from stockbase.stock_core import get_days
from stockbase.stock_db import db_name_to_id


def get_df_ndays(df, ndays):
    # df['date'] = pd.to_datetime(df['date'])
    # print(df.dtypes)
    # print(df.index)
    days = get_days(ndays)
    # t0 = time.time()
    df = df.loc[df['date'].isin(days)]  # 找到60天内数据
    if df.empty:
        return None
    # t1 = time.time()
    # print(t1 - t0)
    df = df.set_index('date')
    return df


def get_kdf_from_pkl(s, isdate=True) -> pd.DataFrame:
    if not isinstance(s, int):
        # print('get pickle error, stock is not int', s)
        temp = s
        s = db_name_to_id(s)
        if s is None:
            print('find stock id error', temp)
            return None

    file = r'..\rawdata\{}.pkl'.format(get_pkl_filename(s))
    if not os.path.exists(file):
        # print('find pkl error', s)
        return None

    f = pd.read_pickle(file)

    for c in f.columns[2:]:
        f[c] = pd.to_numeric(f[c], errors='coerce')
    # f = f.astype(float, errors='ignore')
    # if isdate:
    #     f['date'] = pd.to_datetime(f['date'])
    return f


def get_pkl_filename(s):
    """
    id convert to day file name
    """
    if s is None:
        print('get_pkl_filename error:', s)
        return None

    if isinstance(s, str):
        if len(s) == 8 and s[:2] in ['sh', 'sz']:
            return f'../rawdata/{s[:2]}.{s[2:]}.pkl'

        temp = s
        s = db_name_to_id(s)
        if s is None:
            print('get_pkl_filename error: not found stock id from db:', temp)
            return None

    if not isinstance(s, int):
        print('get_pkl_filename error: input error', s)
        return None

    if s == 300 or s == 999999:
        return 'sh.{0:0>6d}'.format(s)
    if 600000 <= s < 699999:
        return 'sh.{0}'.format(s)
    if s < 10000 or (399999 > s > 300000):
        return 'sz.{0:0>6d}'.format(s)

    # print('get_pkl_filename error: stock over range ', s)
    return None


def get_kdf_from_tdx(s):
    """
    获取tdx日线数据
    """
    file = get_tdx_dayfile(s)
    if file is None or os.path.exists(file):
        print('not found file:', file)
        return None
    reader = TdxDailyBarReader()
    f = reader.get_df(file)
    if f.empty:
        f = None
    return f


def get_tdx_dayfile(s):
    """
    get tdx day file full path
    """
    if isinstance(s, str):
        temp = s
        s = db_name_to_id(s)
        if s is None:
            print('get_tdx_kline_file error: not found stock id from db:', temp)
            return None

    if not isinstance(s, int):
        print('get_tdx_kline_file error: input error', s)
        return None

    if s == 300 or s == 999999:
        file = 'sh{0:0>6d}.day'.format(s)
    elif 600000 <= s < 699999:
        file = 'sh{0}.day'.format(s)
    elif s < 10000 or (399999 > s > 300000):
        file = 'sz{0:0>6d}.day'.format(s)
    else:
        print('get_tdx_kline_file error: stock over range ', s)
        return None

    if file.find('sh') >= 0:
        return r"C:\new_jyplug\vipdoc\sh\lday\{0}".format(file)
    else:
        return r"C:\new_jyplug\vipdoc\sz\lday\{0}".format(file)


def format_df(df):
    df = df.astype(float, errors='ignore')
    df['date'] = pd.to_datetime(df['date'])
    return df


import unittest


class Test_stock_reader(unittest.TestCase):

    def test_readdf(self):

        t0 = time.time()
        for i in range(100):
            df = get_kdf_from_pkl(600036)
            # df = format_pickle(df)
        t = time.time() - t0
        print(t / 100 * 4600)
        print(df.tail(10))
        print(df.columns)
        print(df.dtypes)

        pass

    def test_format_pkl(self):
        pkls = [p for p in os.listdir('../rawdata') if p.endswith('pkl')]
        for p in pkls:
            pklfile = os.path.join('../rawdata', p)
            print(pklfile)
            df = pd.read_pickle(pklfile)
            df = format_df(df)
            df.to_pickle(pklfile)
