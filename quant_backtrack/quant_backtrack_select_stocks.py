import datetime

from quant.quant_backtrack_base import *
from quant.quant_select_stock_base import *
from quant_select_stock.algo2_macross5 import MaCross5


def back_track_select_stocks(select_funs: list[SelectFuncObj]):
    print('start backtrack...', qcfg.track_days)

    days = get_trade_days(qcfg.track_days)

    dayresults = []
    for day in days:

        # calc data offset
        index = days.index(day)
        dayoffset = -len(days) + index + 1
        day = str(day)[:10]
        print(day, index, dayoffset)

        # select stocks
        # select_funs = []
        algo = ''

        print(select_funs, dayoffset, algo)
        results = quant_run_select_stocks(select_funs, dayoffset, algo)

        # get stockids
        stocks: list[int] = [r[0] for r in results]
        if not len(stocks) > 0:
            print(day, 'no stocks')
            dayresults.append('no stocks')
            continue

        # calc next day performance
        startday = dayoffset - 1
        percents = quant_output_probality(stocks, startday)

        quant_select_save(r'E:\STOCKS\stock\output_quant\quant_select_stock_{}_{}.csv'.format(day, algo), results, percents)

        r = quant_select_result_stat(day, stocks, percents)

        dayresults.append(r)

    print('finish select backtracks')

    with open(r'E:\STOCKS\stock\output_quant\quant_select_stock_day_result.csv', 'w', encoding='utf-8') as fs:
        for i in range(len(days)):
            fs.write('{},{}\r\n'.format(days[i], dayresults[i]))
    pass


if __name__ == '__main__':

    qcfg.track_days = 5

    f0 = MaCross5()
    selectfuncs = [f0]

    back_track_select_stocks(selectfuncs)
    pass
