import os.path

from Ashare import *
from eqdata.z_readstocks import *
from eqdata.z_helper import *
from quant.quant_select_stock_base import SelectFuncObj
from stockbase.stock_db import *
from MyTT import *

import numpy as np
import pandas as pd
import time
import math


def RSIP(df):
    C = df.loc[:, 'close']
    C = C.dropna()
    C = pd.to_numeric(C)
    C = np.array(C)
    Z = SMA(MAX(C - REF(C, 1), 0), 6, 1)
    Y = SMA(ABS(C - REF(C, 1)), 6, 1)
    R1 = Y * 5 - Z * 25 + C
    R2 = Y * 5 / 4 - Z * 25 / 4 + C
    R0 = IF(Z / Y < 0.2, R2, R1)
    R = REF(R0, 1)

    return R


class AlgoRsi(SelectFuncObj):
    """
    恐慌价格
    """

    def __init__(self):
        super(AlgoRsi, self).__init__()
        self.desc = '恐慌价格'

        '''恐慌区域阈值'''
        self.rsi_threshold = 10
        '''恐慌判断模式 0-判断恐慌触发，1-恐慌区域判断，2-接近恐慌区域'''
        self.mode = 0
        self.isclose = False
        self.istriggerd = False
        self.rsi = 0

    def run(self, df, stock, dayoffset):

        self.ret = 'rsi error'
        self.isclose = False
        self.istriggerd = False
        self.rsi = 0

        if df.shape[0] < 22:
            self.ret = 'rsi no data'
            return False

        d = df.iloc[dayoffset]
        close = d['close']
        low = d['low']
        if not isinstance(close, float):
            self.ret = 'rsi data float error'
            return False

        # print(stock)
        rsi = RSIP(df)[dayoffset]
        self.rsi = rsi

        delta = round((close - rsi) / close * 100, 2)

        # 接近恐慌区域
        if math.fabs(delta) < self.rsi_threshold:
            self.ret = 'close rsi:{:.2f}-c:{:.2f}-diff:{:.2f}'.format(rsi, close, delta)
            self.isclose = True
            if self.mode == 0:
                # 是否恐慌触发
                if rsi >= low or rsi >= close:
                    self.istriggerd = True
                    self.ret = 'triggered rsi:{:.2f}-c:{:.2f}-diff:{:.2f}'.format(rsi, close, delta)
                    return True
                else:
                    return False
            elif self.mode == 1:
                # 是否接近恐慌
                if rsi >= low or rsi >= close:
                    self.istriggerd = True
                    self.ret = 'triggered rsi:{:.2f}-c:{:.2f}-pct:{:.2f}'.format(rsi, close, delta)
                return True

        self.ret = 'rsi:{:.2f}-c:{:.2f}-diff:{:.2f}'.format(rsi, close, delta)
        return False

    pass


def run_short_rsi(stocks):
    file = 'short'
    # stocks = read_xlsx_codes(file + '.xlsx')

    algo = AlgoRsi()
    algo.mode = 0
    algo.rsi_threshold = 3

    selected = []

    for s in stocks:
        ns = [normalize_code(s)]
        download_rsi_data_60m(ns)

        df = pd.read_pickle('./temp/{}.pkl'.format(s))

        if algo.run(df, int(s), -1):
            selected.append((int(s), algo.ret))
            pass
        if algo.isclose:
            selected.append((int(s), algo.ret))
            print('---close to rsi---')
            print(s, db_id_to_name(s), algo.ret)

    print('-------rsi result--------')
    with open('{}_rsi.csv'.format(file), 'w') as fs:
        for s in selected:
            st = s[0]
            print(st, db_id_to_name(st), s[1])
            fs.write('{},{},{}\n'.format(st, db_id_to_name(st), s[1]))

    return selected
    pass


import unittest


class Test_algo_rsi(unittest.TestCase):

    def test_select_stock(self):
        df = pd.read_pickle(r'./temp/001979.pkl')
        print(df)
        print(df.columns)
        df = df.reset_index()
        print(df)
        print(df.columns)
        df.rename({'': 'date'}, axis=1, inplace=True)
        print(df.columns)
        pass


    def test_rsi(self):
        download_rsi_data_60m([normalize_code('000001')])
        df = pd.read_pickle(r'./temp/000001.pkl')
        dayoffset = 0
        d = df.iloc[-1 + dayoffset]
        close = d['close']
        low = d['low']
        print(close, low)
        r = RSIP(df)[-1 + dayoffset]
        print('rsi', r)

    def test_save_stocks(self):
        file = 'short'
        stocks = read_xlsx_codes(file + '.xlsx')
        print(stocks)
        with open('short.txt', 'w') as fs:
            for s in stocks:
                fs.write('{}\n'.format(s))

    def test_rsi_short_stocks(self):
        stocks = read_txt_code()
        run_short_rsi(stocks)

    def test_rsi_all_stocks(self):
        stocks = db_select_stockcodes()
        run_short_rsi(stocks)


if __name__ == '__main__':

    pass
