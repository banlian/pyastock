import os

import pandas as pd

import datetime
import unittest

from data_util.fetch_data import *
from stockbase.stock_db import db_select_stockids


class Test_Test(unittest.TestCase):

    def test_fetch(self):
        stocks = [
            688630,
            688266,
            301213,
            301199,
            301193,
            301179,
            301168,
            300646,
            300423,
            2752,
        ]

        fetch_stocks(stocks)

    def test_fetch_index(self):
        fetch_index('sh.000001')
        fetch_index('sh.000300')

    def test_readpickl(self):

        f = pd.read_pickle('sh.600036.pkl')
        f = f.tail(1)
        print(f)
        # print(f.dtypes)
        # print(f['date'].dtype == 'datetime64[ns]')

        pass

    def test_check_pickle_files(self):

        stocks = db_select_stockids()
        for s in stocks:
            if not os.path.exists(r'.\{}.pkl'.format(get_stock_pickle_name(s))):
                print(s)
        pass

    def test_check_pickle_empty(self):
        for file in os.listdir('.'):
            if file.find('.pkl') > 0:
                f = pd.read_pickle(file)
                if f.empty:
                    print(file, 'empty')
        pass

    def test_get_frame(self):
        f = get_stock_kline_day_by_pkl(600000)
        # print(f.columns)
        print(f)
        print(f.dtypes)
        for h in f.columns[2:]:
            f[h] = pd.to_numeric(f[h])
        f['date'] = pd.to_datetime(f['date'])
        f['code'] = f['code'].astype('str')
        f = f.tail(60)
        print(f)
        print(f.dtypes)
        print(f.shape)
        print(f.index)
        print(f.iloc[2, :])
        pass

    def test_format_pickle(self):

        index = 1
        for file in os.listdir('.'):
            if file.find('.pkl') > 0 and file.find('table') < 0:
                f = pd.read_pickle(file)
                if f.empty:
                    print(file, 'empty')
                    continue

                if float not in f.dtypes:
                    print('format', file)
                    for h in f.columns[2:]:
                        f[h] = pd.to_numeric(f[h])
                    if f['date'].dtype == 'datetime64[ns]':
                        f['date'] = f['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
                    f['code'] = f['code'].astype('str')
                    f.to_pickle(file)
                    index = index + 1
                    print('format', file, index, 'finish')
                    # break
