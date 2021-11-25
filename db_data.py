import sqlite3

import pandas as pd


def update_market_value():

    df = pd.read_excel(r'.\Table1122.xlsx')
    df.to_pickle('table1122.pkl')

    df = df[['    名称','总市值']]
    print(df)

    conn = sqlite3.connect('stocks.db')

    for r in df.iterrows():
        name = r[1][0]
        if r[1][1] == '--':
            continue
        value = float(r[1][1])/10000000.0 # e

        conn.execute('''update STOCKBASIC set marketvalue = {} where name='{}' '''.format(value, name))

    conn.commit()
    pass


if __name__ == '__main__':

    update_market_value()

    pass