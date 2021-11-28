from plot_multi_stocks import plot_stocks
from quant_base import read_quant_output_stocks
from stock_core import cfg
from stock_reader import get_kdf_from_pkl

import pandas as pd


def get_trade_days(ndays):
    """
        from pick file index 获取交易日
    """
    pkl = pd.read_pickle(r'../rawdata/sh.600000.pkl')
    days = pkl.loc[:, 'date'].values[-ndays:]
    days = list(days)

    return days
    pass

def get_trade_day(dayoff):
    """
        from pick file index 获取交易日
    """
    pkl = pd.read_pickle(r'../rawdata/sh.600000.pkl')
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
