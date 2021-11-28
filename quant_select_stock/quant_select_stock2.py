from quant_select_stock_base import *


class UserSelectAlgo1(SelectFuncObj):
    """
    低位突破
    """

    def __init__(self):
        super(UserSelectAlgo1, self).__init__()
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
        ma201 = factor_ma(df, 20, dayoffset - 1)
        ma301 = factor_ma(df, 30, dayoffset - 1)
        ma601 = factor_ma(df, 60, dayoffset - 1)

        # 5均 10均缠绕
        delta5 = math.fabs(ma5 - ma10) / ma5 * 100 < 3
        delta51 = math.fabs(ma51 - ma101) / ma51 * 100 < 3

        cross5 = ma5 > ma10 and ma51 < ma101
        cross51 = ma5 > ma20 and ma51 < ma201

        # 形态1 地位均线多头 ma5上穿60日先 涨幅大于5 苏澳传感
        type1 = ma5 > ma10 > ma20 and (ma51 < ma601 and ma5 > ma60) and pct > 5
        if type1:
            self.ret = '低位突破1'
            return True

        # 形态2 地位突破 亿纬锂能
        type2 = ma5 > ma10 and ma51 < ma101 and close > ma5 and ma5 < ma20 and ma20 < ma60 and pct > 5
        if type2:
            self.ret = '低位突破2'
            return True

        # 形态2 低位反转 北方稀土
        type2 = ma5 < ma20 and ma51 > ma201 and close > ma5 and ma5 < ma20 and ma20 < ma60 and pct >= 3
        if type2:
            self.ret = '低位反转'
            return True

        return False
        pass


class UserSelectAlgo2(SelectFuncObj):
    """
    高位回踩
    """

    def __init__(self):
        super(UserSelectAlgo2, self).__init__()
        self.desc = '高位回踩'

    def run(self, df, stock, dayoffset):

        mv = marketvalue(stock)
        if not 50 < mv < 20000:
            return False
        pr = price_range_percent(df, 20, dayoffset)
        p = price_increase_percent(df, 20, dayoffset)
        # p2 = price_increase_percent(df, 40, dayoffset)
        if not (10 < p < 50 and 15 < pr < 60):
            return False

        t = turn(df, dayoffset)
        if not 1 < t < 15:
            return False

        row = df.iloc[-1 + dayoffset]

        open = row['open']
        low = row['low']
        high = row['high']

        close = get_prices(df, 1, dayoffset)[0]
        ma5 = factor_ma(df, 5, dayoffset)
        ma10 = factor_ma(df, 10, dayoffset)
        ma20 = factor_ma(df, 20, dayoffset)
        # ma30 = factor_ma(df, 30, dayoffset)
        # ma60 = factor_ma(df, 60, dayoffset)
        #
        # ma51 = factor_ma(df, 5, dayoffset - 1)
        ma101 = factor_ma(df, 10, dayoffset - 1)
        ma201 = factor_ma(df, 20, dayoffset - 1)
        # ma301 = factor_ma(df, 30, dayoffset - 1)

        diff = (close - ma20) / ma20 * 100

        diff10 = ma10 - ma20
        diff101 = ma101 - ma201

        if ma5 < ma10 and ma5 > ma20 \
                and (low < ma20 and open > ma20 and close < ma10) \
                and diff10 < diff101:
            self.ret = '高位回踩'
            return True

        return False
        pass


def quant_select_stock2(off):
    f0 = UserSelectAlgo1()

    funcs = [f0]
    stocks = quant_run_select_stocks(funcs, off, f0.desc)
    stocks = [s[0] for s in stocks]

    # quant_output_probality(stocks, '2021-11-25')

    return stocks
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
    c0 = MaxPercent()
    c0.max_percent = 50
    c0.days = 4

    f0 = UserSelectAlgo2()

    funcs = [f0]

    stocks = quant_run_select_stocks(funcs, 0, f0.desc)

    stocks = [s[0] for s in stocks]

    print(stocks)
    # perces = quant_output_probality(stocks, '2021-11-24', 0)
    # quant_format_percents('1124', stocks, perces)

    pass
