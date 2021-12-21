import pandas as pd

from Ashare import get_price


def get_stock(c):
    try:
        dc = 2
        df = get_price(c, frequency='1d', count=dc)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
        # print('{}60分钟线\n'.format(c), df)
        # df = df.reset_index()
        # df.rename({'': 'date'}, axis=1, inplace=True)
        # print('download', c, ' df', df.shape[0])
        # df.to_pickle('./temp/{}_1m.pkl'.format(c[0:6]))
        # df.to_csv('./temp/{}_1m.csv'.format(c[0:6]))
        if df.empty:
            return None
        return df
    except Exception as ex:
        print('download error', c, ex)
        return None
    pass


def get_stock_pct(c):
    try:
        dc = 2
        df = get_price(c, frequency='1d', count=dc)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
        # print('{}60分钟线\n'.format(c), df)
        # df = df.reset_index()
        # df.rename({'': 'date'}, axis=1, inplace=True)
        # print('download', c, ' df', df.shape[0])
        # df.to_pickle('./temp/{}_1m.pkl'.format(c[0:6]))
        # df.to_csv('./temp/{}_1m.csv'.format(c[0:6]))
        if df.empty or df.shape[0] < 2:
            return 0,0
        c0 = df['close'][-2]
        c1 = df['close'][-1]
        return round((c1 - c0) / c0 * 100, 2),c1
    except Exception as ex:
        print('download error', c, ex)
        return 0,0
    pass


import unittest


class Test_stock(unittest.TestCase):

    def test_get_stock(self):
        d = get_stock('sh000001')
        print(d)
        print(d.dtypes)
        print(d.index)
        d = get_stock('sz399006')
        print(d)
        print(d.dtypes)
        pass

    def test_get_stock2(self):
        d = get_stock_pct('sz300059')
        print(d)
    def test_get_stock3(self):
        d = get_stock_pct('sz002475')
        print(d)

    def test_get_df(self):

        df = pd.read_pickle('./temp/sz002475.pkl')
        print(df)
        df = pd.read_pickle('./temp/sz002475_1m.pkl')
        print(df)