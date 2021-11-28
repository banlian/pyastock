from quant_backtrack_base import *
from quant_select_stock.quant_base_factor import *


class Trade(object):
    capital = 1

    mode = 1


def df_ma(df, ma):
    df1 = df.loc[:, 'close']
    df2 = pd.DataFrame(df1)

    for i in range(0, df1.shape[0] - ma):
        values = df1.iloc[i:i + ma].values
        values = [v for v in values if isinstance(v, float)]
        df2.iloc[ma + i - 1] = sum(values) / len(values)
    return df2
    pass


def trade_ma_func(df: pd.DataFrame, day: int):
    ma5 = factor_ma(df, 5, day)
    ma10 = factor_ma(df, 20, day)
    ma51 = factor_ma(df, 5, day - 1)
    ma101 = factor_ma(df, 20, day - 1)

    if ma5 > ma10 and ma51 < ma101:
        # buy
        return 1
    if ma51 > ma101 and ma5 < ma10:
        # sell
        return -1
    # do nothing
    return 0
    pass


def quant_backtrack_trade(ndays, stock, mode=0):
    days = get_trade_days(ndays)

    captial = 1000000
    buycount = 1000
    hold_stock = 0
    operations = []

    df = get_kdf_from_pkl(stock)

    for d in days:

        doff = -len(days) + days.index(d) + 1
        print(d, doff, '------')

        price = df.iloc[doff]['close']
        if not isinstance(price, float):
            print('stock closed, price:', price)
            continue

        r = trade_ma_func(df, doff)
        if r > 0:
            if captial >= buycount * price:
                operations.append([d, 'buy', r])
                hold_stock = hold_stock + buycount
                captial = captial - buycount * price
                print(d, 'buy', price, 'stock:', hold_stock, 'captial:', captial)
            else:
                print(d, 'not enough money to buy', captial)
        elif r < 0:
            if hold_stock >= buycount:
                operations.append([d, 'sell', r])
                hold_stock = hold_stock - buycount
                captial = captial + buycount * price
                print(d, 'sell', price, 'stock:', hold_stock, 'captial:', captial)
            else:
                print(d, 'no stock for sale', hold_stock)
        else:
            # print(d, 'do nothing')
            pass
        pass

    stock_val = hold_stock * df.iloc[-1]['close']
    print('trade backtrack finish')
    print('capital:', captial)
    print('hold_stocks:', hold_stock)
    print('hold_stocks val:', stock_val)
    print('total:', captial + stock_val)
    print('operation:', operations)

    quant_plot_backtrack_trade(df, ndays, operations)

    pass


import matplotlib.pyplot as plt


def quant_plot_backtrack_trade(df, ndays, operations):
    prices = df.iloc[-ndays:]
    ma5 = df_ma(df, 5)[-ndays:]
    ma10 = df_ma(df, 20)[-ndays:]
    plt.plot(prices['close'], '.-k')
    plt.plot(ma5, '--y')
    plt.plot(ma10, '--c')

    for op in operations:
        date = op[0]
        d = prices.loc[prices['date'] == date]
        if op[2] > 0:
            plt.plot(d.index, d['close'] * 0.999, 'xr')
            plt.text(float(d.index[0]), d['close'] * 0.99, op[1], color='red')
        else:
            plt.plot(d.index, d['close'] * 0.999, '*b')
            plt.text(float(d.index[0]), d['close'] * 0.99, op[1], color='blue')
            pass

    plt.grid('on')
    plt.savefig('quant_backtrack_trade.png')

    pass


if __name__ == '__main__':
    quant_backtrack_trade(90, 600521)

    pass
