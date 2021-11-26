from plot_multi_stocks import plot_stocks
from quant_base import read_quant_output_stocks
from stock_core import cfg
from stock_reader import get_kdf_from_pkl

import pandas as pd

def get_stock_trade_days(ndays):
    """
        from pick file index 获取交易日
    """
    pkl = pd.read_pickle(r'./rawdata/sh.600000.pkl')
    days = pkl.loc[:, 'date'].values[-ndays:]
    days = list(days)

    return days
    pass



def quant_output_probality(stocks: list[int], date='', offset=0):
    """
    计算下一日涨幅
    """
    percents = []
    for s in stocks:
        df = get_kdf_from_pkl(int(s))
        if df is None or df.empty:
            percents.append(0)
            continue
            pass

        d = df.loc[df['date'] == date]

        if d.empty:
            pctChg = 0
        else:
            price0 = df.iloc[d.index, cfg.p_index].values[0]
            if d.index + offset <= df.index[-1]:
                price = df.iloc[d.index + offset, cfg.p_index].values[0]
                pctChg = round((price - price0) / price0 * 100, 2)
            else:
                pctChg = 0
        percents.append(pctChg)

    return percents
    pass


def quant_format_percents(day, stocks, percents, offset=0):
    """
    格式化涨幅数据
    """
    total = sum(percents)
    avg = total / len(percents)
    probility = round(len([p for p in percents if p > 0]) / len(percents) * 100, 2)
    print(day, 'stocks:', len(stocks), 'next', offset, 'day:', 'stat:', total, avg, probility)
    ret = 'find stocks: {} next {} day status: sum: {:.2f} avg:{:.2f} p:{:.2f}'.format(len(stocks), offset, total, avg, probility)
    return ret
    pass


def quant_plot_stocks(file):
    results = read_quant_output_stocks(file)

    cfg.savepath = r'.'
    cfg.algo = 1
    cfg.enable_filter = False
    cfg.ndays = 30
    plot_stocks([r[0] for r in results], '30days')

    pass
