from quant.quant_base_algo import *
from quant.quant_select_stock_base import *


class MA_Increase(SelectFuncObj):

    def __init__(self):
        super(MA_Increase, self).__init__()
        self.date = '2021-11-25'

    def run(self, df, s, off):
        mv = marketvalue(s)
        if not 50 < mv < 300:
            return False

        pr = price_range_percent(df, 15)
        if not 5 < pr < 10:
            return False

        t = turn(df, off)
        if not 5 < t < 10:
            return False

        # 刚进入多头排列
        r1 = algo_ma_inc(df, self.date, -1)
        r2 = algo_ma_inc(df, self.date)
        if not (r1 is False and r2):
            return False

        self.ret = '均线多头mv{}-pr{}-t{}-r1{}-r2{}'.format(mv, pr, t, r1, r2)
        return True
        pass

    pass


if __name__ == '__main__':
    f0 = MA_Increase()
    f0.date = '2021-11-25'

    funcs = [f0]

    stocks = quant_run_select_stocks(funcs, -2, f0.desc)

    stocks = [s[0] for s in stocks]

    print(stocks)

    pass
