from Ashare import get_price
from eqdata.z_readstocks import *


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
                                  symbol.startswith('159') or symbol.startswith('150') or symbol.startswith('123') or
                                  symbol.startswith('16') or symbol.startswith('184801') or
                                  symbol.startswith('201872'))):
        ret_normalize_code = '{}.{}'.format(symbol, EXCHANGE.SZ)
    elif ((len(symbol) == 6) and (symbol.startswith('50') or
                                  symbol.startswith('51') or symbol.startswith('60') or
                                  symbol.startswith('688') or symbol.startswith('900') or
                                  (symbol == '751038'))):
        ret_normalize_code = '{}.{}'.format(symbol, EXCHANGE.SH)
    elif ((len(symbol) == 6) and (symbol[:3] in ['000', '001', '002',
                                                 '200', '300', '301'])):
        ret_normalize_code = '{}.{}'.format(symbol, EXCHANGE.SZ)
    else:
        # print(symbol)
        ret_normalize_code = symbol

    return ret_normalize_code


def download_data_day(codes):
    for c in codes:
        df = get_price(c, frequency='1d', count=360)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
        print('{} 日线\n'.format(c), df)
        df = df.reset_index()
        df.rename({'': 'date'}, axis=1, inplace=True)
        print(df.shape[0])
        df.to_pickle('./temp/{}.pkl'.format(c))
        df.to_csv('./temp/{}.csv'.format(c))


def download_rsi_data_60m(codes):
    for c in codes:
        try:
            dc = 50
            df = get_price(c, frequency='60m', count=dc)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
            # print('{}60分钟线\n'.format(c), df)
            df = df.reset_index()
            df.rename({'': 'date'}, axis=1, inplace=True)
            # print('download', c, ' df', df.shape[0])
            df.to_pickle('./temp/{}.pkl'.format(c[0:6]))
            # df.to_csv('./temp/{}.csv'.format(c[0:6]))
        except Exception as ex:
            print('download error', c, ex)
        pass


def download_rsi_data_1m(codes):
    for c in codes:
        try:
            dc = 5
            df = get_price(c, frequency='1m', count=dc)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
            # print('{}60分钟线\n'.format(c), df)
            df = df.reset_index()
            df.rename({'': 'date'}, axis=1, inplace=True)
            # print('download', c, ' df', df.shape[0])
            df.to_pickle('./temp/{}_1m.pkl'.format(c[0:6]))
            # df.to_csv('./temp/{}_1m.csv'.format(c[0:6]))
        except Exception as ex:
            print('download error', c, ex)
        pass


import unittest


class Test_helper(unittest.TestCase):

    def test_download_index(self):
        download_data_day(['sh000001', 'sh000300'])
        pass

    def test_download_rsi(self):
        stocks = read_txt_code()

        for s in stocks:
            print(normalize_code(s))
            download_rsi_data_60m([normalize_code(s)])
        pass