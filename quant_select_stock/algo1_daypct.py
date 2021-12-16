from quant.quant_select_stock_base import *

import scipy


class MaxPctSlopeDay(SelectFuncObj):
    """
    几日内最大涨幅
    """

    def __init__(self):
        super(MaxPctSlopeDay, self).__init__()
        self.days = 10
        self.slopethreshold = 0.5

    def run(self, df, stock, dayoffset):

        opens = df['open'].iloc[-self.days + dayoffset:]
        closes = df['close'].iloc[-self.days + dayoffset:]

        c1 = float(closes.iloc[-1])
        c0 = float(closes.iloc[0])
        pct = round((c1 - c0) / c0 * 100, 2)

        ma5 = factor_ma(df, 5, dayoffset)
        ma10 = factor_ma(df, 10, dayoffset - self.days)

        p = (opens + closes) / 2
        if len(p) < 2:
            return False

        p0 = p.iloc[0]

        ps = [(pi - p0) / p0 * 100 for pi in p]
        xs = [i * 5 for i in range(len(ps))]

        def linear_fit(x, y):
            """For set of points `(xi, yi)`, return linear polynomial `f(x) = k*x + m` that
            minimizes the sum of quadratic errors.
            """
            meanx = sum(x) / len(x)
            meany = sum(y) / len(y)
            k = sum((xi - meanx) * (yi - meany) for xi, yi in zip(x, y)) / sum((xi - meanx) ** 2 for xi in x)
            m = meany - k * meanx
            return k, m

        slope = linear_fit(xs, ps)[0]
        slope = round(slope, 2)

        if slope > self.slopethreshold and c1 > ma5 and c0 < ma10:
            self.ret = 'max pct slope:{} pct:{}'.format(slope, pct)
            return True
        return False

    pass


class MaxPctDay(SelectFuncObj):
    """
    几日内最大涨幅
    """

    def __init__(self):
        super(MaxPctDay, self).__init__()
        self.days = 3
        self.max_percent = 75

    def run(self, df, s, dayoffset):
        p = price_increase_percent(df, self.days, dayoffset)
        if p >= self.max_percent:
            self.ret = 'days:{} max pct:{:.2f}'.format(self.days, p)
            return True
        return False

    pass


class MostPriceDay(SelectFuncObj):
    """
    几日内最大涨幅
    """

    def __init__(self):
        super(MostPriceDay, self).__init__()
        self.days = 52

    def run(self, df, s, dayoffset):
        opens = df['high'].iloc[-self.days + dayoffset:-1 - dayoffset]

        maxprice = max([float(p) for p in opens])

        close = df['close'].iloc[-1 - dayoffset]

        if close > maxprice:
            self.ret = 'close:{} max:{:.2f}'.format(close, maxprice)
            return True
        return False

    pass


# import unittest
#
#
# class Test_MaxPSelect(unittest.TestCase):
#
#     def test_select(self):
#         df = pd.read_pickle(r'../rawdata/sh.600366.pkl')
#
#         f = MaxPctSlopeDay()
#         f.slopethreshold = 0.66
#         f.days = 5
#         r = f.run(df, 300593, 0)
#         print(r)
#         print(f.ret)
#
#         pass


if __name__ == '__main__':
    """
    查看最近涨的好的股票
    """
    # c0 = MaxPctDay()
    # c0.max_percent = 20
    # c0.days = 8

    c0 = MostPriceDay()
    c0.days = 180

    # c0 = MaxPctSlopeDay()
    # c0.slopethreshold = 0.66
    # c0.days = 6

    quant_run_select_stocks([c0], 0, 'MostPriceDay')

    pass
