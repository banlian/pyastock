


import datetime

import pandas

import os

from db.data_util.helper import *
from stockbase.stock_reader import format_df


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
        o = r['开盘']
        h = r['最高']
        l = r['最低']
        c = r['现价']
        c0 = r['昨收']
        amount = r['总金额']
        vol = r['总手']
        turn = r['换手']
        percent = r['涨幅']

        fcode = format_code(code)
        # print(code, o, h, l, c, c0, vol, amount, turn, percent)

        s = {'date': date,
             'code': fcode,
             'open': o, 'high': h, 'low': l, 'close': c,
             'preclose': c0,
             'volume': vol, 'amount': amount,
             'adjustflag': 2,
             'turn': turn,
             'tradestatus': 1,
             'pctChg': percent,
             'isST': 0
             }

        pklfile = '../rawdata/{}.pkl'.format(fcode)
        csvfile = '../rawdata/{}.csv'.format(fcode)
        if not os.path.exists(pklfile):
            df = pandas.DataFrame(data=s, index=[0])
            df.to_pickle(pklfile)
            df.to_csv(csvfile)
            print('not found', pklfile)
            errors.append(pklfile + 'pkl not exists')
            continue

        # print(df)

        df = pd.read_pickle(pklfile)
        if df.empty:
            print('dateframe empty', fcode)
            df = df.append(s, ignore_index=True)
            dfu = format_df(df)
            dfu.to_csv(csvfile)
            dfu.to_pickle(pklfile)
            errors.append(fcode + ' df empty')
            continue

        d = df.loc[df['date'] == date]
        if not d.empty:
            print('date conflict', fcode)
            df.update(pd.DataFrame(s, index=d.index))
            dfu = format_df(df)
            dfu.to_csv(csvfile)
            dfu.to_pickle(pklfile)
            # update
            if not os.path.exists(csvfile):
                df.to_csv(csvfile)
            continue

        # append to last
        df = df.append(s, ignore_index=True)
        dfu = format_df(df)
        dfu.to_csv(csvfile)
        dfu.to_pickle(pklfile)
        # print('append finish ', fcode)
        print('update', index)

    try:
        with open('fetch_update_data_by_xlsx.log', 'w') as fs:
            for e in errors:
                fs.write(str(e) + '\n')
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


import time


def update_temp_pkls(file, date):
    print(file)
    if not os.path.exists(file):
        print('not exists file', file)
        exit(0)

    print('updating')
    t0 = time.time()
    df = read_ths_xlsx_to_df(os.path.abspath(file))
    update_pickle_by_ths_df(df, date)
    et = time.time() - t0
    print('update elapsed:', et)


if __name__ == '__main__':

    now = datetime.datetime.now()
    date = now.strftime('%m%d')
    dateindex = now.strftime('%Y-%m-%d')
    file = '../temp/Table{}.xls'.format(date)
    print(file, dateindex)

    # df = read_ths_xlsx_to_df(os.path.abspath(file))

    # dateindex = '2021-12-16
    # file = '../temp/Table1216.xlsx'

    # update_temp_pkls(file, dateindex)
    pass
