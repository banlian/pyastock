from quant.quant_base_algo import *
from quant.quant_select_stock_base import *


class MaOrdered(SelectFuncObj):

    def __init__(self, dateindex):
        super(MaOrdered, self).__init__()
        self.date = '2021-11-25'

    def run(self, df, s, off):
        mv = marketvalue(s)
        # if mv < 10:
        #     return False
        #
        # pr = price_range_percent(df, 15)
        # if not 5 < pr < 30:
        #     return False
        #
        # t = turn(df, off)
        # if not 1 < t < 30:
        #     return False

        if off < 0:
            df = df[:off]

        # 刚进入多头排列
        df = df[:off].tail(32)
        ma5 = MA(df['close'], 5)
        ma10 = MA(df['close'], 10)
        ma20 = MA(df['close'], 20)
        ma30 = MA(df['close'], 30)

        inc = ma5[-1] > ma10[-1] > ma20[-1] > ma30[-1]
        inc2 = ma5[-2] > ma10[-2] > ma20[-2] > ma30[-2]
        if not inc or inc2:
            return False

        self.ret = f'mv {mv} maordered {ma5[-1]:.2f} {ma10[-1]:.2f} {ma20[-1]:.2f} {ma30[-1]:.2f}'
        return True
        pass

    pass


if __name__ == '__main__':
    f0 = MaOrdered()
    f0.date = '2021-12-21'

    funcs = [f0]

    stocks = quant_run_select_stocks(funcs, 0, f0.desc)

    stocks = [s[0] for s in stocks]

    print(stocks)

    pass
