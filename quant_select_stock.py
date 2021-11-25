import time

from plot_multi_stocks import plot_dict, plot_stocks
from quant_base import read_quant_output_stocks
from quant_base_db import *
from quant_base_factor import *

from stock_db import *
from stock_reader import *



def algo_ma_inc(df, date='2021-11-24', dayoffset=0):
    """
    均线多头判断
    """
    if df is None:
        print('frame null')
        return False

    d = df[df['date'] == date]
    if not d.empty:
        df = df[:d.index[0] - dayoffset + 1]

        ma5 = factor_ma(df, 5)
        ma10 = factor_ma(df, 10)
        ma20 = factor_ma(df, 20)
        ma30 = factor_ma(df, 30)
        ma60 = factor_ma(df, 60)

        if ma5 >= ma10 and ma10 >= ma20 and ma20 >= ma30 and ma10 >= ma60 and ma20 < ma60:
            # 均线多头
            return True
    # 不选
    return False



def select_stocks_2():
    results = []

    stocks = all_stocksid()
    for s in stocks:
        df = get_kdf_from_pkl(s)
        if df is None or df.empty:
            print('df none', s)
            continue

        p = price_increase_percent(df, 30)
        p2 = price_increase_percent(df, 30)

        close = df.iloc[-1, cfg.p_index]
        ma5 = factor_ma(df, 5)
        ma10 = factor_ma(df, 10)
        ma20 = factor_ma(df, 20)

        if p > 75:
            # if p > 25 and p2 < 50 and close < ma10 and close > ma20:
            results.append([s, p])
            print(s, db_id_to_name(s), p)

    print('found {} stocks!'.format(len(results)))
    print('finish')

    with open('output_quant/quant_select_stock_price_increase.csv', 'w', encoding='utf-8') as fs:
        fs.write('id,stock,pct\r\n')
        for r in results:
            fs.write('{},{},{}\r\n'.format(r[0], db_id_to_name(r[0]), r[1]))
        pass
    pass

    pass


def quant_plot_stocks(file):
    results = read_quant_output_stocks(file)

    cfg.savepath = r'.'
    cfg.algo = 1
    cfg.enable_filter = False
    cfg.ndays = 30
    plot_stocks([r[0] for r in results], '30days')

    pass


def select_stocks(date='2021-11-23'):
    results = []

    stocks = all_stocksid()
    for s in stocks:
        mv = marketvalue(s)
        if not 50 < mv < 300:
            continue

        df = get_kdf_from_pkl(s)
        if df is None or df.empty:
            print('df none', s)
            continue

        pr = price_range_percent(df, 15)
        if not 5 < pr < 10:
            continue

        t = turn(df, date)
        if not 5 < t < 10:
            continue

        # 刚进入多头排列
        r0 = algo_ma_inc(df, date, -2)
        r1 = algo_ma_inc(df, date, -1)
        r2 = algo_ma_inc(df, date)
        if r0 is False and r1 and r2:
            continue

        print('select:', s)
        results.append(s)

    print('found {} stocks!'.format(len(results)))
    print('finish')

    # t = time.strftime('%H-%M-%S')
    # with open(r'.\quant_select_stock_{}.csv'.format(t), 'w', encoding='utf-8') as fs:
    #     for s in results:
    #         fs.write('{}\r\n'.format(db_id_to_name(s)))

    return results
    pass


def calc_probality(stocks, date='', offset=1):
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


def format_percents(day, stocks, percents, offset=1):
    total = sum(percents)
    avg = total / len(percents)
    probility = round(len([p for p in percents if p > 0]) / len(percents) * 100, 2)
    print(day, 'stocks:', len(stocks), 'next', offset, 'day:', 'stat:', total, avg, probility)
    ret = 'find stocks: {} next {} day status: sum: {:.2f} avg:{:.2f} p:{:.2f}'.format(len(stocks), offset, total, avg, probility)
    return ret
    pass


def back_track_select_stocks():
    cfg.p_index = 5

    days = get_days(90)
    days = [d.strftime('%Y-%m-%d') for d in days[:-1] if d.weekday() < 5]

    dayresults = []
    for d in days:
        print(d)

        stocks = select_stocks(d)

        if not len(stocks) > 0:
            print(d, 'no stocks')
            dayresults.append('no stocks')
            continue

        percents = calc_probality(stocks, d, 1)
        # percents2 = calc_probality(stocks, d, 2)

        r = format_percents(d, stocks, percents, 1)
        # r2 = format_percents(percents2, 2)
        dayresults.append(r)

        with open(r'.\quant_select_stock_{}.csv'.format(d), 'w', encoding='utf-8') as fs:
            fs.write('stock,percent,industry\r\n')
            for i in range(len(stocks)):
                fs.write('{},{:.2f},{}\r\n'.format(db_id_to_name(stocks[i]), percents[i], db_id_to_industry(stocks[i]).strip('\r\n')))

            fs.write('{},,\r\n'.format(r))

        # with open(r'quant_select_stock_23-04-56.csv', 'r', encoding='utf-8') as fs:
        #     stocks = fs.readlines()
        #     stocks = [db_name_to_id(s.strip(' \r\n')) for s in stocks]
        #     stocks = [s for s in stocks if s is not None]

    with open('output_quant/quant_select_stock_day_result.csv', 'w', encoding='utf-8') as fs:
        for i in range(len(days)):
            fs.write('{},{}\r\n'.format(days[i], dayresults[i]))
    pass


if __name__ == '__main__':
    cfg.p_index = 5

    #select_stocks_2()

    quant_plot_stocks(r'output_quant/quant_select_stock_price_increase.csv')

    pass
