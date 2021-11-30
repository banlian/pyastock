import datetime
import time

import pandas as pd
from pytdx.reader import TdxDailyBarReader

import unittest
import os


def read_ths_xlsx_to_df(file):
    cols = ['开盘', '最高', '最低', '现价', '昨收', '总金额', '总手', '换手', '涨幅', ]
    df = pd.read_excel(file)
    print(df.columns)
    df = df[['代码', '开盘', '最高', '最低', '现价', '昨收', '总金额', '总手', '换手', '涨幅']]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    print(df)
    print(df.columns)
    print(df.dtypes)
    return df


def update_pickle_by_ths_df(df, date=None):
    if date is None:
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

        s = {'date': date,
             'code': fcode,
             'open': open, 'high': high, 'low': low, 'close': close,
             'preclose': price0,
             'volume': vol, 'amount': amount,
             'adjustflag': 2,
             'turn': turn * 100,
             'tradestatus': 1,
             'pctChg': percent * 100,
             'isST': 0
             }
        # print(df)

        df = pd.read_pickle(pklfile)
        if df.empty:
            print('dateframe empty', fcode)

            dfu = df.append(s, ignore_index=True)
            dfu.to_csv('{}.csv'.format(fcode))
            dfu.to_pickle('{}.pkl'.format(fcode))
            errors.append(fcode)
            continue

        d = df.loc[df['date'] == date]
        if not d.empty:
            print('date conflict', fcode)
            df.update(pd.DataFrame(s, index=d.index))
            df.to_csv('{}.csv'.format(fcode))
            df.to_pickle('{}.pkl'.format(fcode))
            # update
            if not os.path.exists(csvfile):
                df.to_csv(csvfile)
            continue

        # append to last
        dfu = df.append(s, ignore_index=True)
        dfu.to_csv('{}.csv'.format(fcode))
        dfu.to_pickle('{}.pkl'.format(fcode))
        # print('append finish ', fcode)
        print('update', index)

    try:
        with open('fetch_update_data_by_xlsx.log', 'w') as fs:
            for e in errors:
                fs.write(str(e) + '\r\n')
    except Exception as ex:
        print(ex)

    print('update pickle finish')


#
# class Test_Update(unittest.TestCase):
#     def test_readpickl(self):
#         f = pd.read_pickle('sh.688630.pkl')
#         f = f.tail(1)
#         # print(f)
#         # print(f.dtypes)
#         # print(f['date'].dtype == 'datetime64[ns]')
#         pass
#
#     def test_read_xlsx(self):
#         df = read_ths_xlsx_to_df(r'../temp/Table1124.xlsx')
#         df.to_pickle('table1124.pkl')
#         # df = df.iloc[:,['代码','开盘','最高', '最低','现价', '总金额','总手','换手', '涨幅',]]
#
#     def test_update_pkl(self):
#         df = pd.read_pickle('table1124.pkl')
#         update_pickle_by_ths_df(df)
#         pass
#
#     def test_read_tdx_day(self):
#         reader = TdxDailyBarReader()
#         reader.get_df()


def update_pickle():
    xlsxs = [f for f in os.listdir(r'../temp') if f.find('xlsx') > 0]
    for xl in xlsxs:
        date = '2021'+xl[5:9]
        date = datetime.datetime.strptime(date,'%Y%m%d')
        xl = os.path.join(r'..\temp', xl)
        print(xl)

        df = read_ths_xlsx_to_df(xl)
        df.to_pickle(xl[:-5]+'.pkl')
        try:
            update_pickle_by_ths_df(df,date.strftime('%Y-%m-%d'))
        except Exception as ex:
            print(ex)
        print('update finish', xl)


# def update_pickle_data():
#     pickles = [f for f in os.listdir() if f.find('.pkl') > 0]
#     start = pickles.index('sh.600927.pkl')
#     pickles = pickles[start:]
#
#     for pkl in pickles:
#         print(pkl)
#
#         df = pd.read_pickle(pkl)
#         if df.empty:
#             continue
#         if df.iloc[-1, 0] == '2021-11-24':
#             for i in range(4):
#                 df.iloc[-i, 10] = df.iloc[-i, 10] * 100
#
#         df.to_pickle(pkl)
#         df.to_csv(pkl[:-3] + 'csv')


if __name__ == '__main__':
    df = read_ths_xlsx_to_df(os.path.abspath('../temp/Table1130.xlsx'))
    update_pickle_by_ths_df(df, '2021-11-30')
    pass
