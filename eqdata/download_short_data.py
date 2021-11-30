from Ashare import *
from quant_select_stock.quant_select_stock_3_rsi import UserRsiPriceAlgo
from stockbase.stock_db import *


class EXCHANGE(object):
    XSHG = 'XSHG'
    SSE = 'XSHG'
    SH = 'XSHG'
    XSHE = 'XSHE'
    SZ = 'XSHE'
    SZE = 'XSHE'


def normalize_code(symbol, pre_close=None):
    """
    归一化证券代码

    :param code 如000001
    :return 证券代码的全称 如000001.XSHE
    """
    if (not isinstance(symbol, str)):
        return symbol

    if (symbol.startswith('sz') and (len(symbol) == 8)):
        ret_normalize_code = '{}.{}'.format(symbol[2:8], EXCHANGE.SZ)
    elif (symbol.startswith('sh') and (len(symbol) == 8)):
        ret_normalize_code = '{}.{}'.format(symbol[2:8], EXCHANGE.SH)
    elif (symbol.startswith('00') and (len(symbol) == 6)):
        if ((pre_close is not None) and (pre_close > 2000)):
            # 推断是上证指数
            ret_normalize_code = '{}.{}'.format(symbol, EXCHANGE.SH)
        else:
            ret_normalize_code = '{}.{}'.format(symbol, EXCHANGE.SZ)
    elif ((symbol.startswith('399') or symbol.startswith('159') or
           symbol.startswith('150')) and (len(symbol) == 6)):
        ret_normalize_code = '{}.{}'.format(symbol, EXCHANGE.SH)
    elif ((len(symbol) == 6) and (symbol.startswith('399') or
                                  symbol.startswith('159') or symbol.startswith('150') or
                                  symbol.startswith('16') or symbol.startswith('184801') or
                                  symbol.startswith('201872'))):
        ret_normalize_code = '{}.{}'.format(symbol, EXCHANGE.SZ)
    elif ((len(symbol) == 6) and (symbol.startswith('50') or
                                  symbol.startswith('51') or symbol.startswith('60') or
                                  symbol.startswith('688') or symbol.startswith('900') or
                                  (symbol == '751038'))):
        ret_normalize_code = '{}.{}'.format(symbol, EXCHANGE.SH)
    elif ((len(symbol) == 6) and (symbol[:3] in ['000', '001', '002',
                                                 '200', '300'])):
        ret_normalize_code = '{}.{}'.format(symbol, EXCHANGE.SZ)
    else:
        print(symbol)
        ret_normalize_code = symbol

    return ret_normalize_code


def read_codes_nomalized():
    with open('short.txt', 'r', encoding='utf-8') as fs:
        lines = fs.readlines()
        lines = [l.strip('\r\n ') for l in lines]
        lines = [l for l in lines if len(l) > 0]
    return [normalize_code(c) for c in lines]


def read_codes2():
    with open(r'short.txt', 'r', encoding='utf-8') as fs:
        lines = fs.readlines()
        lines = [l.strip('\r\n ') for l in lines]
        lines = [l for l in lines if len(l) > 0]
    return lines


def download_data_60m(codes):
    for c in codes:
        dc = 5 * 4 * 2
        df = get_price(c, frequency='60m', count=dc)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
        print('{}60分钟线\n'.format(c), df)
        df = df.reset_index()
        df.rename({'': 'date'}, axis=1, inplace=True)
        print(df.shape[0])
        df.to_pickle('{}.pkl'.format(c[0:6]))
        df.to_csv('{}.csv'.format(c[0:6]))
        pass

def download_data_day(codes):
    for c in codes:
        df = get_price(c, frequency='1d', count=360)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
        print('{} 日线\n'.format(c), df)
        df = df.reset_index()
        df.rename({'': 'date'}, axis=1, inplace=True)
        print(df.shape[0])
        df.to_pickle('{}.pkl'.format(c))
        df.to_csv('{}.csv'.format(c))

# def read_data2(codes):
#     for c in codes:
#         dc = 5 * 4 * 2
#         df = get_price(c, frequency='60m', count=dc)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
#         print('{}60分钟线\n'.format(c), df)
#         df.to_pickle('{}.pkl'.format(c[0:6]))
#         pass


import unittest


class Test_Data(unittest.TestCase):

    def test_read_code(self):
        codes = read_codes2()
        print(codes)

    def test_download(self):
        download_data_60m(read_codes_nomalized())
        pass
    def test_download_index(self):
        download_data_day(['sh000001','sh000300'])
        pass

    def test_select_stock(self):
        df = pd.read_pickle(r'001979.pkl')
        print(df)
        print(df.columns)
        df = df.reset_index()
        print(df)
        print(df.columns)
        df.rename({'': 'date'}, axis=1, inplace=True)
        print(df.columns)
        pass

    def test_select_stock2(self):
        stocks = read_codes2()

        algo = UserRsiPriceAlgo()
        algo.check_rsi_trigger = False
        algo.rsi_threshold = 5

        selected = []

        for s in stocks:

            df = pd.read_pickle('{}.pkl'.format(s))

            if algo.run(df, int(s), -1):
                selected.append((int(s), algo.ret))
                pass
            print(s, algo.ret)


        print('---------------')
        for s in selected:
            st = s[0]
            print(st, db_id_to_name(st), s[1])