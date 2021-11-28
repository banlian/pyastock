from quant_backtrack.quant_backtrack_base import *
from quant_select_stock_base import *
from stock_reader import get_kdf_from_pkl

from MyTT import *


class UserRsiPriceAlgo(SelectFuncObj):
    """
    恐慌价格
    """

    def __init__(self):
        super(UserRsiPriceAlgo, self).__init__()
        self.desc = '恐慌价格'
        self.rsi_threshold = 10
        self.check_rsi_trigger = True

    def run(self, df, stock, dayoffset):
        mv = marketvalue(stock)
        if not 50 < mv < 5000:
            return False

        if df.shape[0] < math.fabs(dayoffset):
            return False

        d = df.iloc[dayoffset]
        close = d['close']
        low = d['low']
        if not isinstance(close, float):
            print('rsi price error')
            return False

        # print(stock)
        r = RSIP(df)[dayoffset]

        diff = math.fabs(close - r) / close * 100
        self.ret = 'rsi:{:.2f}-c:{:.2f}-pct:{:.2f}'.format(r, close, diff)
        if diff < self.rsi_threshold:
            if self.check_rsi_trigger:
                if low <= r:
                    self.ret = 'triggered rsi:{:.2f}-c:{:.2f}-pct:{:.2f}'.format(r, close, diff)
                    return True
            else:
                if low <= r:
                    self.ret = 'triggered rsi:{:.2f}-c:{:.2f}-pct:{:.2f}'.format(r, close, diff)
                else:
                    self.ret = 'rsi:{:.2f}-c:{:.2f}-pct:{:.2f}'.format(r, close, diff)
                return True

        return False

    pass


def RSIP(df):
    C = df.loc[:, 'close']
    C = C.iloc[:].dropna()
    C = pd.to_numeric(C)
    C = np.array(C)
    Z = SMA(MAX(C - REF(C, 1), 0), 6, 1)
    Y = SMA(ABS(C - REF(C, 1)), 6, 1)
    R1 = Y * 5 - Z * 25 + C
    R2 = Y * 5 / 4 - Z * 25 / 4 + C
    R0 = IF(Z / Y < 0.2, R2, R1)
    R = REF(R0, 1)

    return R


import unittest


class Test_Rsi(unittest.TestCase):

    def test_rsi(self):
        df = get_kdf_from_pkl(2752)

        dayoffset = 0
        d = df.iloc[-1 + dayoffset]
        close = d['close']
        low = d['low']

        print(close, low)
        r = RSIP(df)[-1 + dayoffset]
        print('rsi', r)

    def test_select_rsi(self):
        for i in range(-2, -1):
            dayoff = i
            day = get_trade_day(dayoff)
            print(day)
            results = quant_run_select_stocks([UserRsiPriceAlgo()], dayoff, 'rsi')

            stocks = [int(r[0]) for r in results]
            percents = quant_output_probality(stocks, dayoff)

            quant_select_result_stat(day, stocks, percents)
            quant_select_save('quant_select_stock_rsi_result_{}.csv'.format(day), results, percents)
        pass

    def test_select_output(self):
        dayoff = -2
        day = get_trade_day(dayoff)
        print(day)
        results = read_quant_output_stocks(r'quant_select_stock_rsi_.csv')
        results = [(int(r[0]), r[3]) for r in results]
        stocks = [int(r[0]) for r in results]

        percents = quant_output_probality(stocks, dayoff)

        quant_select_result_stat(day, stocks, percents)
        quant_select_save('quant_select_stock_rsi_result.csv', results, percents)
        pass
