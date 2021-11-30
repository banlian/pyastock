from quant.quant_select_stock_base import *


class MaCross60(SelectFuncObj):
    """
    低位突破
    """

    def __init__(self):
        super(MaCross60, self).__init__()
        self.desc = 'MaCross60'

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
        ma60 = factor_ma(df, 60, dayoffset)

        if close > ma60 and low < ma60 and pct > 3:
            self.ret = 'MaCross60'
            return True

        return False
        pass


class MaCross20(SelectFuncObj):
    """
    低位突破
    """

    def __init__(self):
        super(MaCross20, self).__init__()
        self.desc = 'UserMa20CrossMa30'

    def run(self, df, stock, dayoffset):

        # mv = marketvalue(stock)
        # if not 10 < mv < 5000:
        #     return False

        # 涨幅
        p = price_increase_percent(df, 20, dayoffset)
        if not 5 < p < 30:
            return False

        # 换手
        t = turn(df, dayoffset)
        if not 1 < t < 20:
            return False

        # 振幅
        v = price_range_percent(df, 20, dayoffset)
        if not v < 30:
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

        # 前一日均线
        ma51 = factor_ma(df, 5, dayoffset - 1)
        ma101 = factor_ma(df, 10, dayoffset - 1)
        ma201 = factor_ma(df, 20, dayoffset - 1)
        ma301 = factor_ma(df, 30, dayoffset - 1)

        inc = ma5 > ma10 > ma20
        cross = ma20 >= ma30 and ma201 < ma301
        diff = math.fabs(ma20 - ma30) / ma30 * 100
        diff1 = math.fabs(ma201 - ma301) / ma301 * 100
        nearlycross = diff < 3 and diff < diff1
        if (cross or nearlycross) and inc and pct > 5:
            self.ret = 'ma20crossma30'
            return True

        return False
        pass


class MaCross10(SelectFuncObj):
    """
    低位突破
    """

    def __init__(self):
        super(MaCross10, self).__init__()
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
    f0 = MaCross60()

    funcs = [f0]

    stocks = quant_run_select_stocks(funcs, 0, f0.desc)

    stocks = [s[0] for s in stocks]

    print(stocks)

    pass
