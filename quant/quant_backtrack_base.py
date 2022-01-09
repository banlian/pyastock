from plot_multi_stocks import plot_stocks
from quant.quant_base import read_quant_output_stocks
from stockbase.stock_core import cfg

import pandas as pd


def get_trade_days(ndays):
    """
        from pick file index 获取交易日
    """
    pkl = pd.read_pickle(r'../rawdata/sh.000001.pkl')
    days = pkl.loc[:, 'date'].values[-ndays:]
    days = list(days)

    return days
    pass


def get_trade_days(start, end):
    """
        from pick file index 获取交易日
    """

    pkl = pd.read_pickle(r'../rawdata/sh.000001.pkl')
    days = pkl.loc[:, 'date']
    days = list(days)
    index = days.index(start)
    if index < 0:
        return days

    if end == '':
        return days[index:]
        pass
    else:
        index2 = days.index(end)
        if index2 < 0:
            return days[index:]
        return days[index:index2 + 1]
        pass

    return days
    pass


def get_trade_day(dayoff):
    """
        from pick file index 获取交易日
    """
    pkl = pd.read_pickle(r'../rawdata/sh.000001.pkl')
    days = pkl.loc[:, 'date'].values[dayoff]
    return days
    pass


def quant_plot_stocks(file):
    results = read_quant_output_stocks(file)
    stocks = [r[0] for r in results]

    cfg.savepath = r'.'
    cfg.algo = 1
    cfg.enable_filter = False
    cfg.ndays = 30
    plot_stocks(stocks, '30days')

    pass


import unittest


class Test_Quant(unittest.TestCase):

    def test_get_days(self):
        days = get_trade_days(10)
        print(days)
        pass
