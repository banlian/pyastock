import os.path

from eqdata.z_helper import *
from stockbase.stock_db import *
from MyTT import *

import numpy as np
import pandas as pd
import time
import math


def get_stock_pct(c):
    try:
        df = get_stock_kline(c, freq='1d', count=2)
        if df.empty or df.shape[0] < 2:
            return 0, 0
        c0 = df['close'][-2]
        c1 = df['close'][-1]
        return round((c1 - c0) / c0 * 100, 2), c1
    except Exception as ex:
        print('download error', c, ex)
        return 0, 0
    pass


def get_stock_rsi(c, freq='5m', n=10, count=60):
    try:
        df = get_stock_kline(c, freq=freq, count=count)
        if df.empty or df.shape[0] < 2:
            return 50
        r = get_rsi(df, n)
        return r
    except Exception as ex:
        print('download error', c, ex)
        return 50
    pass


def get_rsi(df, n=10):
    try:
        r = RSI(df['close'], n)
        return r[-1]
    except:
        return math.nan


def get_rsi_price_hour(df):
    C = df['close']
    C = C.dropna()
    C = pd.to_numeric(C)
    C = np.array(C)
    Z = SMA(MAX(C - REF(C, 1), 0), 6, 1)
    Y = SMA(ABS(C - REF(C, 1)), 6, 1)
    R1 = Y * 5 - Z * 25 + C
    R2 = Y * 5 / 4 - Z * 25 / 4 + C
    R0 = IF(Z / Y < 0.2, R2, R1)
    R = REF(R0, 1)

    return R


def run_stocks_rsi(stocks):
    file = 'short'
    # stocks = read_xlsx_codes(file + '.xlsx')
    threshold = 3

    selected = []

    for s in stocks:
        ns = [normalize_code(s)]
        download_rsi_data(ns, '60m')

        df = pd.read_pickle('./temp/{}.pkl'.format(s))
        close = df['close'].values[-1]
        rsi = get_rsi_price_hour(df)[-1]
        delta = round((close - rsi) / close * 100, 2)
        info = f'rsi:{rsi} close:{close}'
        if close < rsi:
            selected.append((int(s), info))
            pass
        elif delta < threshold:
            selected.append((int(s), info))
            print('---close to rsi---')
            print(s, db_id_to_name(s), info)

    print('-------rsi result--------')
    with open('{}_rsi.csv'.format(file), 'w') as fs:
        for s in selected:
            st = s[0]
            print(st, db_id_to_name(st), s[1])
            fs.write('{},{},{}\n'.format(st, db_id_to_name(st), s[1]))

    return selected
    pass


import unittest


class Test_algo_rsi(unittest.TestCase):

    def test_select_stock(self):
        df = pd.read_pickle(r'./temp/001979.pkl')
        print(df)
        print(df.columns)
        df = df.reset_index()
        print(df)
        print(df.columns)
        df.rename({'': 'date'}, axis=1, inplace=True)
        print(df.columns)
        pass

    def test_rsi(self):
        download_rsi_data([normalize_code('000001')], '60m')
        df = pd.read_pickle(r'./temp/000001.pkl')
        dayoffset = 0
        d = df.iloc[-1 + dayoffset]
        close = d['close']
        low = d['low']
        print(close, low)
        r = get_rsi_price_hour(df)[-1 + dayoffset]
        print('rsi', r)

    def test_rsi_short_stocks(self):
        stocks = read_txt_code()
        run_stocks_rsi(stocks)

    def test_rsi_all_stocks(self):
        stocks = db_select_stockcodes()
        run_stocks_rsi(stocks)

    def test_get_stock_rsi(self):
        r = get_stock_rsi('sh510300', n=10, count=60)


        pass


if __name__ == '__main__':

    pass
