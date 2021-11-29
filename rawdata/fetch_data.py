import baostock as bs
import pandas as pd
import sqlite3
import os

from funcy import print_durations


def get_stock_pickle_name(stockid):
    '''
    id convert to day file name
    '''
    if stockid is None:
        print('not found stock id ', stockid)
        return None
    if stockid == 300 or stockid == 999999:
        return 'sh.{0:0>6d}'.format(stockid)
    if stockid >= 600000 and stockid < 699999:
        return 'sh.{0}'.format(stockid)
    if stockid < 10000 or (stockid < 399999 and stockid > 300000):
        return 'sz.{0:0>6d}'.format(stockid)
    return None


@print_durations
def fetch_stocks(stocks):
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    for s in stocks:

        name = get_stock_pickle_name(s)
        if name is None:
            print('stock name error:', name)
            continue

        #### 获取沪深A股历史K线数据 ####
        # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
        # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
        # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
        rs = bs.query_history_k_data_plus(name,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date='2018-01-01',
                                          # end_date='2017-12-31',
                                          frequency="d", adjustflag="2")
        print('query_history_k_data_plus respond error_code:' + rs.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        #### 结果集输出到csv文件 ####
        result.to_pickle('{}.pkl'.format(name))
        # result.to_csv(name, index=False)
        print(s, 'success', result.empty, result.shape[0])

    #### 登出系统 ####
    bs.logout()
    print('logout')


def fetch_index(name):
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    if name:
        #### 获取沪深A股历史K线数据 ####
        # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
        # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
        # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
        rs = bs.query_history_k_data_plus(name,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date='2018-01-01',
                                          # end_date='2017-12-31',
                                          frequency="d", adjustflag="2")
        print('query_history_k_data_plus respond error_code:' + rs.error_code)
        print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        #### 结果集输出到csv文件 ####
        result.to_pickle('{}.pkl'.format(name))
        result.to_csv('{}.csv'.format(name))
        # result.to_csv(name, index=False)
        print(name, 'success', result.empty, result.shape[0])

    #### 登出系统 ####
    bs.logout()
    print('logout')


def get_stocks_from_db():
    conn = sqlite3.connect(r'../stockbase/stocks.db')

    return [s[0] for s in conn.execute('select number from stocks').fetchall()]


def get_stock_kline_day_by_pkl(s):
    if not isinstance(s, int):
        print('get pickle error, stock is not int', s)

    file = r'.\{}.pkl'.format(get_stock_pickle_name(s))
    if not os.path.exists(file):
        print('find pickel error', s)
        return None

    return pd.read_pickle(file)


import datetime
import unittest


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

        conn = sqlite3.connect(r'../stockbase/stocks.db')
        stocks = [s[0] for s in conn.execute('''select number from stocks''').fetchall()]
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
            if file.find('.pkl') > 0:
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


if __name__ == '__main__':
    stocks = get_stocks_from_db()
    print(stocks)

    fetch_stocks(stocks)

    print('save data finish')
    pass
