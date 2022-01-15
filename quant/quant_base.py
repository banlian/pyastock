import datetime

from stockbase.stock_core import cfg
from stockbase.stock_db import *
from stockbase.stock_reader import *


class qcfg(object):
    track_days = 30


def quant_output_probality(stocks: list[int], offset=-1):
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

        if offset < -1:
            d = df.iloc[offset:]
            if d.empty:
                pctChg = 0
            else:
                price0 = float(d.iloc[offset, cfg.p_index])
                price1 = float(d.iloc[offset + 1, cfg.p_index])
                pctChg = round((price1 - price0) / price0 * 100, 2)
        else:
            pctChg = 0

        percents.append(pctChg)

    return percents
    pass


def quant_select_result_stat(day, stocks, percents):
    """
    格式化涨幅数据
    """
    # 总计
    total = sum(percents)
    # 平均涨幅
    avg = total / len(percents)
    # 胜率
    probility = round(len([p for p in percents if p > 0]) / len(percents) * 100, 2)

    ret = 'find stocks: {} next day status: sum: {:.2f} avg:{:.2f} p:{:.2f}'.format(len(stocks), total, avg, probility)
    print(day, ret)
    return ret
    pass


def quant_select_save(file, results, percents=None):
    if percents is None or len(percents) == 0:
        with open(file, 'w', encoding='utf-8') as fs:
            fs.write('id,stock,industry,info\n')
            for r in results:
                fs.write('{},{},{},{}\n'.format(r[0], db_id_to_name(r[0]), db_id_to_industry(r[0]), r[1]))
            pass
            # fs.write(file)

    else:
        with open(file, 'w', encoding='utf-8') as fs:
            fs.write('id,stock,industry,info,percents\r\n')
            for r in results:
                fs.write('{},{},{},{},{}\n'.format(r[0], db_id_to_name(r[0]), db_id_to_industry(r[0]), r[1], percents[results.index(r)]))

            fs.write(quant_select_result_stat('', [r[0] for r in results], percents) + '\n')
            pass
            # fs.write(file)
    pass


def read_quant_output_stocks(file):
    with open(file, 'r', encoding='utf-8') as fs:
        lines = fs.readlines()[1:]
        lines = [l.strip('\r\n') for l in lines if len(l.strip('\r\n')) > 0]

    results = []
    for l in lines[:]:
        vals = l.split(',')
        results.append(vals)

    return results


def get_day_offset(date):
    d0 = datetime.datetime.today()
    d1 = datetime.datetime.strptime(date, '%Y-%m-%d')
    return (d1 - d0).days


import unittest


class Test_QuantBase(unittest.TestCase):

    def test_dayoffset(self):
        d0 = datetime.datetime.strptime('2021-11-11', '%Y-%m-%d')

        d1 = datetime.datetime.strptime('2021-11-26', '%Y-%m-%d')
        d1 = datetime.datetime.today()

        offset = d0 - d1
        print(offset)
        print(offset.days)

    def test_getdayoffset(self):
        print(get_day_offset('2021-11-11'))

    def test_quant_select_result(self):
        print(quant_output_probality([600036], -2))
        print(quant_output_probality([600036], -1))
        print(quant_output_probality([600036], 0))
