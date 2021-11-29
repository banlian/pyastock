import datetime
import time

from dateutil.relativedelta import relativedelta
import pandas as pd


def get_days(ndays):
    days = []
    end = datetime.datetime.today()
    for i in range(ndays):
        day = datetime.datetime.today() - datetime.timedelta(days=i)
        days.append(datetime.datetime(day.year,day.month,day.day))
    days.reverse()
    return days


import unittest


class Test_T(unittest.TestCase):

    def test_days(self):
        days = get_days(60)

        print(days)
        print(min(days))
        print(max(days))

    def test_get_df_ndays(ndays):
        df = pd.read_pickle(r'../rawdata/sh.600036.pkl')
        print(df.dtypes)
        df['date'] = pd.to_datetime(df['date'])
        # print(df.dtypes)
        # print(df.index)

        days = get_days(22)
        t0 = time.time()
        df = df.loc[df['date'].isin(days)]

        t1 = time.time()
        print(t1 - t0)
        # print(df)
        df = df.set_index('date')
        print(df.index)

        print(df.loc[datetime.datetime(2021, 11, 22)])

        pass


if __name__ == '__main__':
    pass
