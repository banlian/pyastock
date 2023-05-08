from MyTT import *
from quant.quant_select_stock_base import *


class Ma60Triggered(SelectFuncObj):
    def __init__(self):
        super().__init__()

        self.desc = f'ma60trigger'

    def run(self, df, stock, dayoffset):
        if df is None:
            return False
        if df.empty or df.shape[0] < 120:
            return False

        try:
            closes = df['close'].dropna()
            lows = df['low'].dropna()
            low = lows.values[-1]
            close = closes.values[-1]
            ma60 = MA(closes, 60)
            ma = ma60[-1]
            rsi = RSI(closes, 10)
            r = rsi[-1]

            # mar = ma60[-5:]<=ma+0.01
            # print(low, close, ma, r)
            if low < ma and close > ma and r < 40:
                self.ret = f'ma60_{ma}_rsi_{r}'
                return True
        except Exception as ex:
            print(stock, ex)
            raise RuntimeError()
            return False
        return False

        pass


if __name__ == '__main__':
    f0 = Ma60Triggered()

    funcs = [f0]

    stocks = quant_run_select_stocks(funcs, 0, f0.desc)

    print(stocks)

    pass
