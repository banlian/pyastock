
import datetime

class qcfg(object):

    track_days = 30



def read_quant_output_stocks(file):
    with open(file, 'r', encoding='utf-8') as fs:
        lines = fs.readlines()[1:]
        lines = [l.strip('\r\n') for l in lines if len(l.strip('\r\n'))>0]

    results = []
    for l in lines[1:]:
        vals = l.split(',')
        results.append((int(vals[0]), vals[1]))

    return results


def get_day_offset(date):
    d0 = datetime.datetime.today()
    d1 = datetime.datetime.strptime(date,'%Y-%m-%d')
    return (d1-d0).days


import unittest
class Test_QuantBase(unittest.TestCase):

    def test_dayoffset(self):

        d0 = datetime.datetime.strptime('2021-11-11', '%Y-%m-%d')

        d1 = datetime.datetime.strptime('2021-11-26', '%Y-%m-%d')
        d1 = datetime.datetime.today()

        offset = d0-d1
        print(offset)
        print(offset.days)

    def test_getdayoffset(self):

        print(get_day_offset('2021-11-11'))