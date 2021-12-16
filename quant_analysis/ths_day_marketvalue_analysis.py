import sqlite3

import pandas as pd


def update_market_value():
    df = pd.read_excel(r'..\temp\Table1216.xlsx')
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


def select_market_value(mv):
    conn = sqlite3.connect('../stocks.db')
    ret = conn.execute('''select count(*) from STOCKBASIC where marketvalue > {}'''.format(mv)).fetchall()
    return ret[0][0]


if __name__ == '__main__':

    update_market_value()

    mv = [10000, 2000, 1000, 500, 250, 150, 100, 50, 0]
    mvcount = [select_market_value(v) for v in mv]

    with open('day_marketvalue.csv', 'w') as fs:

        fs.write('marketvalue, count\n')

        for i in range(len(mv)):
            mvi = mv[i]
            mvcounti = mvcount[i]
            print('mv > {} count {}'.format(mvi, mvcounti))
            # if i > 0:
            #     print('{} > mv > {} count {}'.format(mv[i - 1], mvi, mvcounti - mvcount[i - 1]))
            fs.write('{},{}\n'.format(mvi, mvcounti))
            pass
