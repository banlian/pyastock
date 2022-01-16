import os

from Ashare import get_price

import pandas as pd


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


def download_rsi_data(codes, freq='5m', count=60):
    for c in codes:
        try:
            df = get_price(c, frequency=freq, count=count)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
            # print('{}60分钟线\n'.format(c), df)
            df = df.reset_index()
            if 'day' in df.columns:
                df.rename({'day': 'date'}, axis=1, inplace=True)
            else:
                df.rename({'': 'date'}, axis=1, inplace=True)
            # print('download', c, ' df', df.shape[0])
            df.to_pickle('./temp/{}_{}.pkl'.format(c, freq))
            # df.to_csv('./temp/{}.csv'.format(c))
        except Exception as ex:
            os.remove('./temp/{}_{}.pkl'.format(c, freq))
            print('download error', c, ex)
        pass


def read_codes_nomalized():
    with open('short.txt', 'r', encoding='utf-8') as fs:
        lines = fs.readlines()
        lines = [l.strip('\r\n ') for l in lines]
        lines = [l for l in lines if len(l) > 0]
    return [normalize_code(c) for c in lines]


def get_stock_kline(s, freq='1d', count=2):
    try:
        if len(s) == 6:
            s = normalize_code(s)

        df = get_price(s, frequency=freq, count=count)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
        # df = df.reset_index()
        # df.rename({'': 'date'}, axis=1, inplace=True)
        # df.to_pickle('./temp/{}_1m.pkl'.format(c[0:6]))
        # df.to_csv('./temp/{}_1m.csv'.format(c[0:6]))
        if df.empty:
            return None
        return df
    except Exception as ex:
        print('download error', s, ex)
        return pd.DataFrame()
    pass




def read_txt_code(file):
    with open(file, 'r', encoding='utf-8') as fs:
        lines = fs.readlines()
        lines = [l.strip('\r\n ') for l in lines]
        lines = [l for l in lines if len(l) > 0]
    return lines


def read_xlsx_codes(excelfile):
    if excelfile.endswith('xls'):
        df = pd.read_csv(excelfile, encoding='gbk', sep='\t')
        txtfile = excelfile[:-3] + 'txt'
        print('read csv success')
    elif excelfile.endswith('xlsx'):
        df = pd.read_excel(excelfile)
        txtfile = excelfile[:-4] + 'txt'
        print('read excel success')
    else:
        raise NotImplementedError('file format')
    df = df.iloc[:, 0]
    codes = [str(r).lower() for r in df.values if len(str(r)) == 8]

    with open(txtfile, 'w') as fs:
        for c in codes:
            fs.write('{}\n'.format(c))
    pass

    return codes




import unittest


class Test_helper(unittest.TestCase):

    def test_download_index(self):
        download_data_day(['sh000001', 'sh000300'])
        pass

    def test_normalizecode(self):

        print(normalize_code('600036'))

    def test_download_rsi(self):
        stocks = read_txt_code('short.txt')

        for s in stocks:
            print(normalize_code(s))
            download_rsi_data([normalize_code(s)], '60m')
        pass

    def test_read_code(self):
        codes = read_txt_code()
        print(codes)

    def test_read_xlsx_code(self):
        df = pd.read_excel('short.xlsx')

        df = df['代码']
        df.reset_index()
        df.to_csv('short.pkl')

    def test_read_pkl_codes(self):
        codes = read_xlsx_codes('short.xls')
        print(codes)
        codes = read_xlsx_codes('shortz.xls')
        print(codes)

    def test_xls(self):
        df = pd.read_csv('short.xls', encoding='gbk', sep='\t')
        print(df)
        print(df.columns)
        print(df.index)
