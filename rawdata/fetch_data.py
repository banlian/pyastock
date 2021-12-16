import time

import baostock as bs
import pandas as pd
import os

from stockbase.stock_db import *

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

        t0 = time.time()

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
        result.to_csv('{}.csv'.format(name))

        et = time.time() - t0
        # result.to_csv(name, index=False)
        print(stocks.index(s), 'stock:', s, 'success', et, result.empty, result.shape[0])

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

        t0 = time.time()
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

        et = time.time() - t0
        # result.to_csv(name, index=False)
        print('stock:', name, 'success', et, result.empty, result.shape[0])

    #### 登出系统 ####
    bs.logout()
    print('logout')


def get_stock_kline_day_by_pkl(s):
    if not isinstance(s, int):
        print('get pickle error, stock is not int', s)

    file = r'.\{}.pkl'.format(get_stock_pickle_name(s))
    if not os.path.exists(file):
        print('find pickel error', s)
        return None

    return pd.read_pickle(file)


if __name__ == '__main__':
    # stocks = db_select_stockids()
    # print(stocks)

    fetch_index('sh.000001')
    fetch_index('sh.000300')

    #fetch_stocks(stocks)

    print('save data finish')
    pass
