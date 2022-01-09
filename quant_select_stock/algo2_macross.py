from quant.quant_select_stock_base import *

from MyTT import *


class MaSequence(SelectFuncObj):
    def __init__(self, ndays=5):
        super(MaSequence, self).__init__()
        self.ndays = ndays
        self.desc = 'Sequence'
        pass

    def run(self, df, stock, dayoffset):

        opens = df['open'][-self.ndays - 2:]
        closes = df['close'][-self.ndays - 2:]

        ret = closes > opens

        rets = ret[-self.ndays:]
        rets2 = ret[-self.ndays - 1:]

        if all(rets) == True and all(rets2) == False:
            return True
        return False

        pass


class MaCloseCross(SelectFuncObj):
    """
    低位突破
    """

    def __init__(self):
        super(MaCloseCross, self).__init__()
        self.desc = 'maclosecross'

    def run(self, df, stock, dayoffset):

        # 当日数据
        row = df.iloc[-1 + dayoffset]
        open = row['open']
        low = row['low']
        high = row['high']
        close = row['close']
        pct = row['pctChg']

        # 均线
        ma5 = factor_ma(df, 5, dayoffset)
        ma10 = factor_ma(df, 10, dayoffset)
        ma20 = factor_ma(df, 20, dayoffset)
        ma30 = factor_ma(df, 30, dayoffset)

        if close > ma5 and close > ma10 and close > ma20 and close > ma30 and low < ma5:
            self.ret = 'maclosecross by{:.2f}'.format(pct)
            return True

        return False
        pass


class MaCross60(SelectFuncObj):
    """
    低位突破
    """

    def __init__(self):
        super(MaCross60, self).__init__()
        self.ma = 60
        self.desc = 'macross{}'.format(self.ma)

    def run(self, df, stock, dayoffset):
        # mv = marketvalue(stock)
        # if not 10 < mv < 5000:
        #     return False

        # 涨幅
        # p = price_increase_percent(df, 20, dayoffset)
        # if not 5 < p < 50:
        #     return False
        #
        # # 换手
        # t = turn(df, dayoffset)
        # if not 1 < t < 20:
        #     return False
        #
        # # 振幅
        # v = price_range_percent(df, 20, dayoffset)
        # if not v < 50:
        #     return False

        # 当日数据
        row = df.iloc[-1 + dayoffset]
        open = row['open']
        low = row['low']
        high = row['high']
        close = row['close']
        pct = row['pctChg']

        # 均线
        m = factor_ma(df, self.ma, dayoffset)
        m1 = factor_ma(df, self.ma, dayoffset - 1)

        if close > m and low < m and pct > 3 and m > m1:
            self.ret = 'macross{} by{:.2f}'.format(self.ma, pct)
            return True

        return False
        pass


class MaCross2(SelectFuncObj):
    """
    低位突破
    """

    def __init__(self):
        super(MaCross2, self).__init__()
        self.desc = '低位突破'

    def run(self, df, stock, dayoffset):

        mv = marketvalue(stock)
        if not 10 < mv < 500:
            return False

        # 涨幅
        p = price_increase_percent(df, 20, dayoffset)
        if not 10 < p < 30:
            return False

        # 换手
        t = turn(df, dayoffset)
        if not 1 < t < 20:
            return False

        # 振幅
        v = price_range_percent(df, 20, dayoffset)
        if not v < 25:
            return False

        # 当日数据
        row = df.iloc[-1 + dayoffset]
        open = row['open']
        low = row['low']
        high = row['high']
        close = row['close']
        pct = row['pctChg']

        # 均线
        ma5 = factor_ma(df, 5, dayoffset)
        ma10 = factor_ma(df, 10, dayoffset)
        ma20 = factor_ma(df, 20, dayoffset)
        ma30 = factor_ma(df, 30, dayoffset)
        ma60 = factor_ma(df, 60, dayoffset)

        # 前一日均线
        ma51 = factor_ma(df, 5, dayoffset - 1)
        ma101 = factor_ma(df, 10, dayoffset - 1)

        # 5均 10均缠绕
        delta5 = math.fabs(ma5 - ma10) / ma5 * 100 < 3
        cross5 = ma5 > ma10 and ma51 < ma101

        # 形态1 地位均线多头 ma5上穿60日先 涨幅大于5 苏澳传感
        type1 = ma5 > ma10 > ma20 and (cross5 or delta5) and pct > 5
        if type1:
            self.ret = '低位突破10'
            return True

        return False
        pass


#
# class TestQuantSelect(unittest.TestCase):
#
#     def test_selec(self):
#         cfg.p_index = 5
#         df = get_kdf_from_pkl(301060)
#
#         print(get_prices(df, 3))
#
#         print(price_increase_percent(df, 3))
#
#         pass
#
#     def test_user_select(self):
#
#         f = UserSelectAlgo2()
#
#         r=f.run(get_kdf_from_pkl(603283), 603283, 0)
#         print(r)
#
#         pass

if __name__ == '__main__':
    f0 = MaSequence()
    f0.ndays = 3

    # f0 = MaCloseCross()

    funcs = [f0]

    stocks = quant_run_select_stocks(funcs, 0, f0.desc)

    stocks = [s[0] for s in stocks]

    print(stocks)

    pass
