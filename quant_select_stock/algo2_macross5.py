from quant.quant_select_stock_base import *

from MyTT import *


class MaCross5(SelectFuncObj):
    """
    5日线cross
    """

    def __init__(self):
        super(MaCross5, self).__init__()
        self.ma0 = 3
        self.ma1 = 20
        self.desc = 'ma{}cross{}'.format(self.ma0, self.ma1)

    def run(self, df, stock, dayoffset):
        mv = marketvalue(stock)
        if not 10 < mv < 50000:
            return False

        # # # 涨幅
        p = price_increase_percent(df, 20, dayoffset)
        if not 5 < p < 50:
            return False
        #
        # # 换手
        t = turn(df, dayoffset)
        if not 0.5 < float(t) < 30:
            return False
        #
        # # 振幅
        # v = price_range_percent(df, 20, dayoffset)
        # if not v < 30:
        #     return False

        # 当日数据
        row = df.iloc[-1 + dayoffset]
        # open = row['open']
        # low = row['low']
        # high = row['high']
        close = float(row['close'])
        pct = float(row['pctChg'])

        if dayoffset == 0:
            df = df.iloc[-1 + dayoffset - 200:, cfg.p_index]
        else:
            df = df.iloc[-1 + dayoffset - 200: dayoffset, cfg.p_index]

        df = pd.to_numeric(df)

        # 均线
        ma0 = RSI(df, 6)
        # ma1 = MA(df, 20, )
        ma5 = ma0[-1]
        # ma10 = factor_ma(df, self.ma1, dayoffset)

        # 前一日均线
        ma51 = ma0[-2]
        ma52 = ma0[-3]
        # ma101 = factor_ma(df, self.ma1, dayoffset - 1)

        cross = ma52 > ma51 and ma51 < ma5 and ma5 < 55
        # cross = ma5 >= ma10 and ma51 < ma101
        if cross:
            s = SLOPE(df[-100:], 60)
            # sma = SLOPE(ma0[-4:], 3)
            if 0.1 <= s[-1] < 1:
                self.ret = 'cross by close {:.2f} ma {:.2f} pct {:.2f} slope:{:.2f}'.format(close, ma5, pct, s[-1])
                return True

        return False
        pass


if __name__ == '__main__':
    f0 = MaCross5()

    funcs = [f0]

    stocks = quant_run_select_stocks(funcs, 0, f0.desc)

    stocks = [s[0] for s in stocks]

    print(stocks)

    pass
