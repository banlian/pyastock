from quant.quant_base import *
from quant.quant_base_db import *
from quant.quant_base_factor import *
from stockbase.stock_db import *
from stockbase.stock_reader import *


class SelectFuncObj(object):
    def __init__(self):
        self.name = type(self).__name__
        self.desc = ''
        self.ret = ''

    def run(self, df, stock, dayoffset):
        return True


class MarketValLimit(SelectFuncObj):
    """
    市值
    """

    def __init__(self):
        super(MarketValLimit, self).__init__()
        self.minval = 10
        self.maxval = 1000

    def run(self, df, s, dayoffset):
        mv = marketvalue(s)
        if self.minval <= mv <= self.maxval:
            return True
        return False

    pass


class MaCross(SelectFuncObj):
    """
    均线穿越
    """

    def __init__(self):
        super(MaCross, self).__init__()
        self.ma0 = 5
        self.ma1 = 10
        self.above = True

    def run(self, df, stock, dayoffset):
        ma0v = factor_ma(df, self.ma0, dayoffset)
        ma1v = factor_ma(df, self.ma1, dayoffset)
        ma0v1 = factor_ma(df, self.ma0, dayoffset - 1)
        ma1v1 = factor_ma(df, self.ma1, dayoffset - 1)

        if self.above:
            # 上穿
            if ma0v >= ma1v and ma0v1 < ma1v1:
                return True
        else:
            # 下穿
            if ma0v < ma1v and ma0v1 >= ma1v1:
                return True
        return False


class AboveMa(SelectFuncObj):
    def __init__(self):
        super(AboveMa, self).__init__()
        self.ma = 5
        pass

    def run(self, df, stock, dayoffset):
        ma = factor_ma(df, self.ma, dayoffset)
        p = get_prices(1, dayoffset)[0]
        if p >= ma:
            return True
        return False


def quant_run_select_stocks(func_list: list[SelectFuncObj], dayoffset: int, algo='default'):
    """
    量化选股
    """
    results = []

    stocks = all_stocksid()

    info = '-'.join([f.desc for f in func_list])
    print('run', info)

    day = datetime.datetime.today()

    for s in stocks:
        df = get_kdf_from_pkl(s)
        if df is None or df.empty:
            print('df none', s)
            continue

        day = df['date'].iloc[-1 + dayoffset]
        if stocks.index(s) == 0:
            print('quant select date:', day)

        r = True
        for f in func_list:
            if not f.run(df, s, dayoffset):
                r = False
                break

        if not r:
            continue

        if len(func_list) > 1:
            results.append([s, '-'.join([f.ret for f in func_list])])
        else:
            results.append([s, func_list[0].ret])

        print(s, db_id_to_name(s))

    print('\n{}\nfound {} stocks!'.format(info, len(results)))
    print('finish')

    quant_select_save('quant_select_stock_{}_{}.csv'.format(algo, day.strftime('%Y-%m-%d')), results)

    return results
    pass


# import unittest
#
#
# class Test_QuantBase(unittest.TestCase):
#
#     def test_select(self):
#         quant_run_select_stocks([MaxPercent()], -2, '', '')
#         pass
