import os
import pandas as pd

from stockbase.stock_db import db_id_to_name

import matplotlib.pyplot as plt


def read_ths_xlsx_to_df(file):
    cols = ['开盘', '最高', '最低', '现价', '昨收', '总金额', '总市值', '总手', '换手', '涨幅', ]
    df = pd.read_excel(file)
    # print(df.columns)
    df = df[['代码', '开盘', '最高', '最低', '现价', '昨收', '总金额', '总市值', '总手', '换手', '涨幅']]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    # print(df)
    # print(df.columns)
    # print(df.dtypes)

    return df


def analysis_day_vol(file):
    df = read_ths_xlsx_to_df(file)
    df.to_pickle('day.pkl')
    # df: pandas.DataFrame = pd.read_pickle('day.pkl')

    c_vol = '总金额'
    c_mv = '总市值'
    df[c_vol] = df[c_vol] / 1e8
    df[c_mv] = df[c_mv] / 1e8
    dvol = df[df[c_vol] > 0]

    # 按市值排名
    dvol = dvol.sort_values(by=c_mv, ascending=False)

    totalvol = sum(dvol[c_vol])

    def mostvol(h):
        ret = dvol.head(h)
        return sum(ret[c_vol])

    ret = dvol.head(50)
    print(file)

    mvols = []

    print('total:', totalvol)

    for i in [50, 100, 250, 500, 1000]:
        mi = round(mostvol(i),2)
        mvols.append(mi)
        print('most{}:'.format(i), mi, round(mi / totalvol * 100))

    with open('{}_most40.csv'.format(file), 'w') as fs:
        for i, r in ret.iterrows():
            name = r[0]
            symbol = db_id_to_name(int(name[2:]))
            vol = r[c_vol]
            fs.write('{},{},{}\n'.format(name, symbol, vol))

    return totalvol, mvols, file


def multi_days_vol():
    files = [f for f in os.listdir('../temp') if f.endswith('xlsx')]

    print(files)
    results = []
    for f in files:
        ret = analysis_day_vol(os.path.join('../temp', f))
        results.append(ret)

    indexs = range(len(results))

    with open('day_vol.csv', 'w') as fs:
        for r in results:
            fs.write('{},{},{},{}\n'.format(r[2], r[1][0], r[0], round(r[1][0] / r[0] * 100, 2)))

    plt.plot(indexs, [r[0] for r in results], '-x')
    plt.plot(indexs, [r[1][0] for r in results], '-or')
    plt.plot(indexs, [r[1][1] for r in results], '-or')
    plt.plot(indexs, [r[1][2] for r in results], '-or')
    plt.plot(indexs, [r[1][3] for r in results], '-or')
    plt.plot(indexs, [r[1][4] for r in results], '-or')
    plt.grid(color='k', linestyle='dotted', linewidth=1)
    plt.savefig('total-most.png')
    pass


def day_vol_hist(file):
    # df = read_ths_xlsx_to_df(file)
    # df.to_pickle('day.pkl')
    df: pd.DataFrame = pd.read_pickle('day.pkl')

    c_vol = '总金额'
    c_mv = '总市值'
    df[c_vol] = df[c_vol] / 1e8
    df[c_mv] = df[c_mv] / 1e8

    dvol = df[df[c_vol] > 0]
    dvol = dvol.sort_values(by=c_mv, ascending=False)
    totalvol = sum(dvol[c_vol])
    print(totalvol)

    # 市值前1000占成交额一半
    dvol = dvol.head(1000)
    vols = dvol[c_vol]
    mostvol = sum(vols)
    print(mostvol)
    print(round(mostvol / totalvol * 100, 2))

    plt.hist(vols, bins=50)
    plt.grid()
    plt.show()


if __name__ == '__main__':

    file = '../temp/Table1216.xlsx'
    analysis_day_vol(file)
    day_vol_hist(file)
    pass
