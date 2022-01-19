import math

import pandas as pd
import sqlite3

from data_util.fetch_update_data_by_xlsx import *
from stockbase.stock_db import db_select_stockcodes


def update_db_marketvalue(df):
    df = df[['代码', '总市值']]
    # print(df)

    conn = sqlite3.connect('../stocks.db')

    for r in df.iterrows():
        name = r[1][0][2:]
        value = float(r[1][1]) / 1e8  # e
        if r[1][1] == '--' or math.isnan(value):
            # print('skip', name, value)
            continue
        # print('update', name, value)
        conn.execute('''update STOCKBASIC set marketvalue = {} where symbol={} '''.format(value, int(name)))

    conn.commit()
    conn.close()
    pass


def update_db_stocks(df):
    stocks = df.iloc[:, 0]
    thsstocks = [s for s in stocks.values]
    print(f'ths xls stocks {len(thsstocks)}')
    # print(thsstocks)

    dbstocks = db_select_stockcodes()
    print(f'dbstocks {len(dbstocks)}')
    # print(dbstocks)

    conn = sqlite3.connect('../stocks.db')

    for s in thsstocks:
        if s[2:] not in dbstocks:
            tscode = f'{s[2:]}.{s[:2]}'
            row = df[df['代码'] == s]
            # print(row)
            symbol = int(s[2:])
            name = row['    名称'].values[0]
            ind = row['所属行业'].values[0]
            mv = row['总市值'].values[0]
            print('insert new stock:', tscode, symbol, name, ind, mv)

            conn.execute('''insert into STOCKBASIC (ts_code, symbol, name, industry, ind2) values ('{}',{},'{}','{}','{}')'''
                         .format(tscode, symbol, name, ind, ind))

    conn.commit()
    conn.close()

    dbstocks = db_select_stockcodes()
    print(f'dbstocks {len(dbstocks)}')

    print('udpate market value finish')

    pass


def update_misc(df):
    def ts_code(code):
        if len(code) == 8:
            return f'{code[2:]}.{code[:2]}'
        else:
            return ''

    conn = sqlite3.connect('../stocks.db')

    for i, row in df.iterrows():
        code = row.loc['代码']
        bk = row.loc['细分行业']
        pe = row.loc['TTM市盈率']
        pb = row.loc['市净率']
        # print(code, bk, pe, pb)
        if math.isnan(pe):
            pe = 0
        if math.isnan(pb):
            pb = 0
        tc = ts_code(code)
        if len(tc) == 9:
            conn.execute('''update STOCKBASIC set pe={}, pb={}, bk='{}' where ts_code = '{}' '''.format(pe, pb, bk, tc))
            # conn.commit()
            # print(f'update {i} {tc} {pe} {pb} {bk}')
        # break
    conn.commit()
    conn.close()


if __name__ == '__main__':

    now = datetime.datetime.now()
    date = now.strftime('%m%d')
    dateindex = now.strftime('%Y-%m-%d')

    # date = '0107'
    # dateindex = '2022-01-07'

    file = '../temp/Table{}.xls'.format(date)
    print(file, dateindex)

    df = read_ths_xlsx_to_df(file)

    # 更新股票
    update_db_stocks(df)

    # 更新市值
    update_db_marketvalue(df)

    # 更新 pe pb bk
    update_misc(df)

    print('update all finish')
    pass
