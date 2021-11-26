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

    print('start backtrack...')
    qcfg.track_days = 2

    days = get_stock_trade_days(qcfg.track_days)

    dayresults = []
    for date in days:

        # calc data offset
        index = days.index(date)
        off = -len(days) + index + 1
        print(date, off)

        # select stocks
        select_funs = [UserSelectAlgo1()]
        algo = ''

        results = quant_run_select_stocks(select_funs, off, '1', date)
        quant_select_save(r'.\output_quant\quant_select_stock_{}_{}.csv'.format(date, algo), results)

        # get stockids
        stocks: list[int] = [r[0] for r in results]
        if not len(stocks) > 0:
            print(date, 'no stocks')
            dayresults.append('no stocks')
            continue

        # calc next day performance
        nextday = 1
        percents = quant_output_probality(stocks, date, nextday)

        r = quant_format_percents(date, stocks, percents, nextday)

        dayresults.append(r)

    print('finish select backtracks')

    with open('output_quant/quant_select_stock_day_result.csv', 'w', encoding='utf-8') as fs:
        for i in range(len(days)):
            fs.write('{},{}\r\n'.format(days[i], dayresults[i]))
    pass


if __name__ == '__main__':
    back_track_select_stocks()
    pass
