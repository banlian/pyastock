import time

import pandas as pd
from pytdx.reader import TdxDailyBarReader

import unittest
import os


class Test_Update(unittest.TestCase):
    def test_readpickl(self):
        f = pd.read_pickle('sh.688630.pkl')
        f = f.tail(1)
        # print(f)
        # print(f.dtypes)
        # print(f['date'].dtype == 'datetime64[ns]')
        pass

    def test_read_xlsx(self):
        excelfile = r'..\Table1122.xlsx'

        cols = ['开盘', '最高', '最低', '现价', '昨收', '总金额', '总手', '换手', '涨幅', ]
        df = pd.read_excel(excelfile)
        print(df.columns)
        df = df[['代码', '开盘', '最高', '最低', '现价', '昨收', '总金额', '总手', '换手', '涨幅']]
        for c in cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        print(df)
        print(df.columns)
        print(df.dtypes)
        df.to_pickle('table1122.pkl')
        # df = df.iloc[:,['代码','开盘','最高', '最低','现价', '总金额','总手','换手', '涨幅',]]

    def test_read_pkl(self):
        df = pd.read_pickle('table1122.pkl')
        print(df.columns)
        print(df.dtypes)

        date = time.strftime('%Y-%m-%d')
        print(date)

        def format_code(c):
            if c >= 600000 and c < 699999:
                return 'sh.{:0>6d}'.format(c)
            if c < 10000 or (c < 399999 and c > 300000):
                return 'sz.{:0>6d}'.format(c)
            return 'sh.{:0>6d}'.format(c)

        errors = []

        for index, r in df.iterrows():
            code = int(r['代码'][2:])
            open = r['开盘']
            high = r['最高']
            low = r['最低']
            close = r['现价']
            price0 = r['昨收']
            amount = r['总金额']
            vol = r['总手']
            turn = r['换手']
            percent = r['涨幅']

            fcode = format_code(code)
            # print(code, open, high, low, close, price0, vol, amount, turn, percent)

            pklfile = '{}.pkl'.format(fcode)
            csvfile = '{}.csv'.format(fcode)
            if not os.path.exists(pklfile):
                print('not found', pklfile)
                errors.append(pklfile)
                continue

            df = pd.read_pickle(pklfile)
            if df.empty:
                print('dateframe empty', fcode)
                errors.append(fcode)
                continue
            if df.iloc[-1, 0] == date:
                print('date confilict', fcode)
                if not os.path.exists(csvfile):
                    df.to_csv(csvfile)
                continue
            s = {'date': date, 'code': fcode, 'open': open, 'high': high, 'low': low, 'close': close,
                 'preclose': price0, 'volume': vol, 'amount': amount,
                 'turn': turn, 'pctChg': percent}
            # print(df)
            df = df.append(s, ignore_index=True)
            df.to_csv('{}.csv'.format(fcode))
            df.to_pickle('{}.pkl'.format(fcode))
            print('update', fcode)
            # print(df)

        print('update pickle finish')
        pass

    def test_read_tdx_day(self):
        reader = TdxDailyBarReader()
        reader.get_df()

    def test_update_pickle(self):
        pass


if __name__ == '__main__':
    # read_xlsx()

    pass
