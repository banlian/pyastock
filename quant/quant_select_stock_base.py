import time

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


def get_df(s):
    return get_kdf_from_pkl(s)
    pass

def get_df2(s):
    file = f'{s}_1w.pkl'
    df = pd.read_pickle(f'../etrade_track/temp/{file}.pkl')
    return df
    pass


def quant_run_select_stocks(func_list: list[SelectFuncObj] = [], dayoffset: int = -1, algo='default', stocks=None):
    """
    量化选股
    """
    results = []

    stocks = db_select_tscodes() if stocks is None else stocks

    info = '-'.join([f.desc for f in func_list])
    print('run', info)
    algo = algo + '_' + info
    print('algo', algo)

    day = datetime.datetime.today()

    t0 = time.time()

    for s in stocks:
        df = get_df(s)
        if df is None or df.empty:
            print('df none', s)
            continue

        if df.shape[0] < abs(dayoffset) + 1:
            print('df shape short', s)
            continue

        day = df['date'].iloc[-1 + dayoffset]
        if stocks.index(s) == 0:
            print('quant select date:', day)

        r = True
        for f in func_list:
            if not f.run(df, int(s[2:]), dayoffset):
                r = False
                break

        if not r:
            continue

        if len(func_list) > 1:
            results.append([s, '-'.join([f.ret for f in func_list])])
        else:
            results.append([s, func_list[0].ret])

        # print(s, db_id_to_name(s))

    et = time.time() - t0

    print(f'\n{info}\nfound {len(results)} in {len(stocks)} stocks by {et.real:.2f} s !')
    print('finish')

    quant_select_save(f'quant_select_stock_{algo}_{day.strftime("%Y-%m-%d")}.csv', results)

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
