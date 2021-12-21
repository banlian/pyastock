import pandas as pd
import sqlite3

from data_util.fetch_update_data_by_xlsx import read_ths_xlsx_to_df


def update_db_marketvalue(excelfile):
    df = read_ths_xlsx_to_df(excelfile)
    df = df[['代码', '总市值']]
    print(df)

    conn = sqlite3.connect('../stocks.db')

    for r in df.iterrows():
        name = r[1][0][2:]
        if r[1][1] == '--':
            continue
        value = float(r[1][1]) / 100000000.0  # e

        conn.execute('''update STOCKBASIC set marketvalue = {} where symbol={} '''.format(value, int(name)))

    conn.commit()
    pass

