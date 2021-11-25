from stock_core import cfg
import pandas as pd
import math
import numpy as np
from pandas import DataFrame

from stock_core import *
from stock_reader import get_kdf_from_pkl


def factor_ma(df, ndays, offset=-1):
    data = df.iloc[-ndays + offset + 1:offset, cfg.p_index].values
    data = [d for d in data if isinstance(d, float)]
    return sum(data) / len(data)
    pass


def factor_max_price(df, ndays, offset=-1):
    data = df.iloc[-ndays + offset + 1:offset, cfg.p_index].values
    data = [d for d in data if isinstance(d, float)]
    return max(data)
    pass


def factor_min_price(df, ndays, offset=-1):
    data = df.iloc[-ndays + offset + 1:offset, cfg.p_index].values
    data = [d for d in data if isinstance(d, float)]
    return max(data)
    pass


def price_range_percent(df, ndays=20, offset=-1):
    prices = df.iloc[-ndays + offset + 1:offset, cfg.p_index].values
    prices = [float(p) for p in prices if isinstance(p, float)]
    pmax = max(prices)
    pmin = min(prices)
    prange = pmax - pmin
    pavg = sum(prices) / len(prices)
    return round(prange / pavg, 2) * 100


def price_var_percent(df, ndays=20, offset=-1):
    prices = df.iloc[-ndays + offset + 1:offset, cfg.p_index].values
    prices = [float(p) for p in prices if isinstance(p, float)]

    pavg = sum(prices) / len(prices)
    poffs = [p - pavg for p in prices]
    pvar = np.var(poffs)
    return round(pvar[0], 2)


def price_std_percent(df, ndays=20, offset=-1):
    prices = df.iloc[-ndays + offset + 1:offset, cfg.p_index].values
    prices = [float(p) for p in prices if isinstance(p, float)]

    pavg = sum(prices) / len(prices)
    poffs = [p - pavg for p in prices]
    pvar = np.std(poffs)
    return round(pvar[0], 2)


def price_increase_percent(df, ndays=20, offset=-1):
    prices = df.iloc[-ndays + offset + 1:offset, cfg.p_index].values
    prices = [float(p) for p in prices if isinstance(p, float)]

    pct = (prices[-1] - prices[0]) / prices[0]
    return round(pct, 2) * 100



import unittest


class TestSelect(unittest.TestCase):

    def test_ma5(self):
        cfg.p_index = 5
        df = get_kdf_from_pkl(688728)
        v = factor_ma(df, 5)
        print(v)
        v = factor_ma(df, 10)
        print(v)
        v = factor_ma(df, 20)
        print(v)
        pass
