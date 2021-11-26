from typing import List, Union, Any

import pandas as pd

from quant_backtrack_base import *
from quant_select_stock_base import *
from quant_select_stock1 import *
from quant_select_stock2 import *

from stock_core import cfg, get_days
from stock_db import db_id_to_name, db_id_to_industry


def back_track_select_stocks():
    cfg.p_index = 5
    #
    # days = get_days(90)
    # days = [d.strftime('%Y-%m-%d') for d in days[:-1] if d.weekday() < 5]
    #
    # 获取交易日
    #
    qcfg.track_days = 2
    pkl = pd.read_pickle(r'./rawdata/sh.600000.pkl')
    days = pkl.loc[:, 'date'].values[-qcfg.track_days:]
    days = list(days)

    print('start backtrack...')

    dayresults = []
    for d in days:
        index = days.index(d)
        off = -len(days) + index + 1
        print(d, off)

        results = quant_run_select_stocks([UserSelectAlgo1()], off, '1', d)
        stocks: list[int] = [r[0] for r in results]

        if not len(stocks) > 0:
            print(d, 'no stocks')
            dayresults.append('no stocks')
            continue

        percents = quant_output_probality(stocks, d, 1)
        r = quant_format_percents(d, stocks, percents, 1)

        dayresults.append(r)

        with open(r'.\output_quant\quant_select_stock_{}.csv'.format(d), 'w', encoding='utf-8') as fs:
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
    back_track_select_stocks()
    pass
