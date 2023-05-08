from quant.quant_select_stock_base import *


class Ma20Retest(SelectFuncObj):
    """
    高位回踩
    """

    def __init__(self):
        super(Ma20Retest, self).__init__()
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


if __name__ == '__main__':
    f0 = Ma20Retest()

    funcs = [f0]

    stocks = quant_run_select_stocks(funcs, -1, f0.desc)

    stocks = [s[0] for s in stocks]

    print(stocks)

    pass
