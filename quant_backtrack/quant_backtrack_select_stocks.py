from quant.quant_backtrack_base import *
from quant_select_stock.quant_select_stock2 import *


def back_track_select_stocks():

    print('start backtrack...', qcfg.track_days)

    days = get_trade_days(qcfg.track_days)

    dayresults = []
    for day in days:

        # calc data offset
        index = days.index(day)
        select_date = -len(days) + index + 1
        print(day, select_date)

        # select stocks
        select_funs = [UserSelectAlgo1()]
        algo = ''

        results = quant_run_select_stocks(select_funs, select_date, algo, day)

        # get stockids
        stocks: list[int] = [r[0] for r in results]
        if not len(stocks) > 0:
            print(day, 'no stocks')
            dayresults.append('no stocks')
            continue

        # calc next day performance
        nextday = select_date+1
        percents = quant_output_probality(stocks, nextday)

        quant_select_save(r'.\output_quant\quant_select_stock_{}_{}.csv'.format(day, algo), results, percents)

        r = quant_select_result_stat(day, stocks, percents)

        dayresults.append(r)

    print('finish select backtracks')

    with open('../output_quant/quant_select_stock_day_result.csv', 'w', encoding='utf-8') as fs:
        for i in range(len(days)):
            fs.write('{},{}\r\n'.format(days[i], dayresults[i]))
    pass


if __name__ == '__main__':
    back_track_select_stocks()
    pass
