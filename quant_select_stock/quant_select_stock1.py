from quant_base_db import *
from quant_base_factor import *
from quant_base_algo import *
from quant_select_stock_base import *


class UserSelecFunc(SelectFuncObj):

    def __init__(self):
        super(UserSelecFunc, self).__init__()
        self.date = '2021-11-25'

    def run(self, df, s):
        mv = marketvalue(s)
        if not 50 < mv < 300:
            return False

        pr = price_range_percent(df, 15)
        if not 5 < pr < 10:
            return False

        t = turn(df, self.date)
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


def quant_select_stock1(d):

    pass

if __name__ == '__main__':
    us = UserSelecFunc()
    us.date = '2021-11-25'

    quant_run_select_stocks([us])
    pass
