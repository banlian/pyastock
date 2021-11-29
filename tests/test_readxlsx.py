import sqlite3
import pandas as pd

dbfile = 'stock/stocks.db'


def read_xls():
    df = pd.read_excel(r'沪深Ａ股20211120.xlsx')
    df.to_pickle('a_stocks.pkl')
    print(df.head())


def read_stocks():
    conn = sqlite3.connect(dbfile)
    ret = conn.execute('''select distinct industry from stockbasic''').fetchall()
    print(ret)
    with open('../ind.txt', 'w') as fs:
        for r in ret:
            fs.write('{}'.format(str(r[0]).encode('utf').decode('utf')))
            fs.write('\r\n')
    pass


def update_industry_from_tdx_xlsx():
    df = pd.read_pickle('../a_stocks.pkl')
    # print(df)
    frame = df.iloc[:, [0, 1, 13]]
    conn = sqlite3.connect(dbfile)

    except_st = []

    for index, row in frame.iterrows():
        print(index)
        try:
            conn.execute('''update stockbasic set ind2 = '{}' where symbol = '{}' '''.format(row[2], row[0]))
        except Exception as ex:
            except_st.append(row)
            pass
        # break
    conn.commit()
    conn.close()
    print('------------')


def read_user():
    dict = {}

    with open('../analysis_user.txt', 'r', encoding='utf8') as f:
        lines = f.readlines()
        lines = [l.strip('\r\n ') for l in lines]
        lines = [l for l in lines if len(l) > 0]
        print(lines)

        state = 'indict'
        dlist = []
        dname = lines[0][1:].strip()

        for l in lines[1:]:
            if l.find('#') >= 0:
                dict[dname] = dlist
                dname = l[1:].strip()
                dlist = []
            else:
                dlist.append(l)
            pass

    return dict
    pass


import unittest
import math
import matplotlib.pyplot as plt


class Test_User(unittest.TestCase):

    def test_readuser(self):
        '''read user dict from file'''
        u = read_user()
        print(u)
        pass

    def test_algo_price_amount_ratio(self):
        '''
        成交量爆量 造成 ratio值偏差过大

        '''

        res = 0.05
        x = [i*res for i in range(0,100)]
        y = [math.atan(i * res)*1.2732395447351628 for i in range(0,100)]

        plt.plot(x, y, '.-')
        plt.grid('on')
        plt.show()

        pass


    def test_read_pickle(self):
        f = pd.read_pickle('../a_stocks.pkl')
        print(f)
        pass


if __name__ == '__main__':
    pass
