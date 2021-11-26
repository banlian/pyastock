from stock_core import cfg
import pandas as pd
import math
import numpy as np
from pandas import DataFrame

from stock_core import *
from stock_reader import get_kdf_from_pkl


def get_prices(df, ndays, offset: int = 0):
    if offset >= 0:
        data = df.iloc[(-ndays + offset):, cfg.p_index].values
    elif offset < 0:
        data = df.iloc[(-ndays + offset):offset, cfg.p_index].values
    data = [d for d in data if isinstance(d, float)]
    return data


def get_df_rows(df, offset: int = 0):
    if offset >= 0:
        data = df.iloc[(-1 + offset):]
    elif offset < 0:
        data = df.iloc[(-1 + offset):offset]
    return data


def turn(df, offset: int = 0):
    """
    换手率
    """
    df = df.iloc[(-1 + offset)]
    return df['turn']


def amount(df, offset: int = 0):
    """
    成交量
    """
    df = df.iloc[(-1 + offset)]
    return df['amount']


def factor_ma(df, ndays, offset: int = 0):
    data = get_prices(df, ndays, offset)
    if len(data) < 1:
        return 0
    return sum(data) / len(data)
    pass


def factor_max_price(df, ndays, offset: int = 0):
    data = get_prices(df, ndays, offset)
    if len(data) < 1:
        return 0
    return max(data)
    pass


def factor_min_price(df, ndays, offset: int = 0):
    data = get_prices(df, ndays, offset)
    if len(data) < 1:
        return 0
    return min(data)
    pass


def price_range_percent(df, ndays=20, offset=0):
    if offset >= 0:
        data = df.iloc[(-ndays + offset):]
    elif offset < 0:
        data = df.iloc[(-ndays + offset):offset]
    if data is not None and data.empty:
        return 0
    pmax = max([v for v in data['high'].values if isinstance(v, float)])
    pmin = min([v for v in data['low'].values if isinstance(v, float)])
    prange = pmax - pmin
    return round(prange / pmin, 2) * 100


def price_mean(df, ndays=20, offset=0):
    prices = get_prices(df, ndays, offset)
    if len(prices) < 1:
        return 0
    pavg = sum(prices) / len(prices)
    return round(pavg, 3)


def price_var_percent(df, ndays=20, offset=0):
    prices = get_prices(df, ndays, offset)
    if len(prices) < 1:
        return 0
    pavg = sum(prices) / len(prices)
    poffs = [p - pavg for p in prices]
    pvar = np.var(poffs)
    return round(pvar, 2)


def price_std_percent(df, ndays=20, offset=0):
    prices = get_prices(df, ndays, offset)
    if len(prices) < 1:
        return 0
    pavg = sum(prices) / len(prices)
    poffs = [p - pavg for p in prices]
    pvar = np.std(poffs)
    return round(pvar, 2)


def price_increase_percent(df, ndays=20, offset=0):
    prices = get_prices(df, ndays, offset)
    if len(prices) < ndays:
        return 0
    pct = (prices[-1] - prices[0]) / prices[0]
    return round(pct, 2) * 100


import unittest


class TestSelect(unittest.TestCase):

    def test_ma5(self):
        cfg.p_index = 5
        df = get_kdf_from_pkl(688728)
        v = factor_ma(df, 5, -1)
        print(v)
        v = factor_ma(df, 5, 0)
        print(v)
        v = factor_ma(df, 10)
        print(v)
        v = factor_ma(df, 20)
        print(v)
        pass

    def test_var(self):
        cfg.p_index = 5
        df = get_kdf_from_pkl(688728)

        print(get_prices(df, 5))
        v = price_mean(df, 5)
        print(v)

        v = price_range_percent(df, 5)
        print(v)

        v = price_increase_percent(df, 5)
        print(v)

        v = price_var_percent(df, 5)
        print(v)

        v = price_std_percent(df, 5)
        print(v)
