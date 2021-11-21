from funcy import print_durations

import time
import math

import matplotlib.pyplot as plt
import sqlite3
import os
from pytdx.reader import TdxDailyBarReader

from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

width, height = 25, 12.5
plt.rcParams['figure.figsize'] = width, height

# 通达信日K数据的收盘价索引
p_index = 3
a_index = 5

algo = 3


def calc_frame_price(frame):
    if algo == 1:
        r = base_price_algo(frame)
    elif algo == 2:
        r = price_percentage_algo(frame, False)
    elif algo == 3:
        r = price_percentage_algo(frame, True)
    else:
        r = raw_price_algo(frame)
    return r
    pass


def raw_price_algo(frame):
    '''
    convert price into base price percentage
    相对起始价格的涨幅不能很好展示每天的涨幅和波动情况
    不能体现股价高位时的波动 高位波动大 但相对初始价格波动较小
    '''
    prices = frame.iloc[:, p_index]
    p0 = prices[0]
    # print('base price', p0)
    for i in range(len(prices)):
        frame.iloc[i, p_index] = round((prices[i] - p0) / p0 * 100, 2)
    pass
    return 'raw'


def base_price_algo(frame):
    '''
    convert price into base price percentage
    相对起始价格的涨幅不能很好展示每天的涨幅和波动情况
    不能体现股价高位时的波动 高位波动大 但相对初始价格波动较小
    '''
    prices = frame.iloc[:, p_index]
    p0 = prices[0]
    # print('base price', p0)

    for i in range(len(prices)):
        frame.iloc[i, p_index] = round((prices[i] - p0) / p0 * 100, 2)
    pass

    return 'baseprice'


def center_of_mass_algo(frame):
    """
    计算股价重心
    """
    prices = frame.iloc[:, p_index]
    amount = frame.iloc[:, a_index]

    p0 = prices[0]

    percents = []

    # calc center of mass
    for i in range(1, len(prices)):
        amountfactor = amount[i] / amount[i - 1]
        # 防止爆量造成 factor 过大
        # atan 0-1基本线性 收敛于2
        amountfactor = math.atan(amountfactor) * 1.27

        percents.append(round((prices[i] - prices[i - 1]) / prices[i - 1] * 100 * amountfactor, 2))
    pass

    # assign mass
    for i in range(len(prices)):
        if i > 0:
            frame.iloc[i, p_index] = sum(percents[:i + 1])
        else:
            frame.iloc[i, p_index] = 0

    pass


def price_percentage_algo(frame, is_amount):
    '''
    convert price into base price percentage
    涨跌幅相加算法
    无法体现股价实际高低情况 涨幅可体现股价波动  涨幅*成交量因子？低的更低 高的更高
    '''
    prices = frame.iloc[:, p_index]
    amount = frame.iloc[:, a_index]

    p0 = prices[0]
    # print('base price', p0)

    percents = [0, ]

    if is_amount:
        # 计算当日涨跌幅*成交量因子
        for i in range(1, len(prices)):
            amountfactor = amount[i] / amount[i - 1]
            # 防止爆量造成 factor 过大
            # atan 0-1基本线性 收敛于2
            amountfactor = math.atan(amountfactor) * 1.27
            percents.append(round((prices[i] - prices[i - 1]) / prices[i - 1] * 100 * amountfactor, 2))
        pass
    else:
        # 计算当日涨跌幅
        for i in range(1, len(prices)):
            percents.append(round((prices[i] - prices[i - 1]) / prices[i - 1] * 100, 2))

    for i in range(len(prices)):
        if i > 0:
            frame.iloc[i, p_index] = sum(percents[:i + 1])
        else:
            frame.iloc[i, p_index] = 0
    pass

    return 'percentage_amount' if is_amount else 'percentage'


def get_tdx_kline_file(stock):
    '''
    get tdx day file full path
    '''
    if stock.find('sh') >= 0:
        return r"C:\new_jyplug\vipdoc\sh\lday\{0}".format(stock)
    else:
        return r"C:\new_jyplug\vipdoc\sz\lday\{0}".format(stock)


def db_name_to_id(name):
    '''
    find stock id from db name-id dict
    '''
    with sqlite3.connect('stocks.db') as conn:

        db = conn.execute(
            '''select NUMBER from stocks where NAME = '{0}' '''.format(name))

        res = db.fetchall()

        if len(res) > 0:
            return res[0][0]
        else:
            return None


def db_id_to_name(id):
    '''
    find stock id from db name-id dict
    '''
    with sqlite3.connect('stocks.db') as conn:
        db = conn.execute(
            '''select NAME from stocks where NUMBER = {0} '''.format(id))
        res = db.fetchall()

        if len(res) > 0:
            return res[0][0]
        else:
            return str(id)


def tdx_id_to_klinefile(stockid):
    '''
    id convert to day file name
    '''
    if stockid is None:
        print('not found stock id ', stockid)
        return None
    if stockid == 300 or stockid == 999999:
        return 'sh{0:0>6d}.day'.format(stockid)
    if stockid >= 600000 and stockid < 699999:
        return 'sh{0}.day'.format(stockid)
    if stockid < 10000 or (stockid < 399999 and stockid > 300000):
        return 'sz{0:0>6d}.day'.format(stockid)
    return None


def find_stock_kline_file(s):
    if isinstance(s, str):
        file = tdx_id_to_klinefile(db_name_to_id(s))
    elif isinstance(s, int):
        file = tdx_id_to_klinefile(s)
    else:
        print('find_stock_kline_file error: ', s)
        return None

    if file is None:
        print('find_stock_kline_file error: not found', s)
        return None
    return get_tdx_kline_file(file)


def get_stock_kline_day_dataframe(s):
    '''
    获取tdx日线数据
    '''
    file = find_stock_kline_file(s)
    if file is None or os.path.exists(file):
        print('not found file:', file)
        return None
    reader = TdxDailyBarReader()
    return reader.get_df(file)


@print_durations()
def plot_stocks(stocks, ndays=90, title='', savepath='.'):
    '''
    plot multi stocks k line in one figure
    '''

    # 强制最后比较沪深300指数
    stocks.append(300)

    reader = TdxDailyBarReader()

    plt.clf()
    ax = plt.gca()
    # ax.spines['left'].set_color('none')
    # ax.spines['right'].set_color('none')
    # ax.spines['top'].set_color('none')
    # plt.ylim(-1,1)
    # plt.xlim(0,10)
    # ax.spines['bottom'].set_position(('data',0))
    maloc = plt.MultipleLocator(5)
    miloc = plt.MultipleLocator(1)
    ax.yaxis.set_major_locator(maloc)
    ax.yaxis.set_minor_locator(miloc)
    # maloc = plt.MultipleLocator(10)
    # miloc = plt.MultipleLocator(5)
    # ax.xaxis.set_major_locator(maloc)
    # ax.xaxis.set_minor_locator(miloc)

    for s in stocks:

        file = find_stock_kline_file(s)
        if file is None or not os.path.exists(file):
            print('not found', file)
            continue

        try:
            df = reader.get_df(file)
            df = df.tail(ndays)
        except:
            print('read frame error', file)
            continue
            pass

        # print(df)
        # print('before modify')
        # print(df.iloc[:,p_index])
        # print('-------------------------------')

        # return algo name
        price_algo = calc_frame_price(df)
        # print('-------------------------------')
        # print('after modify')
        # print(df.iloc[:,p_index])
        # exit(0)
        # print(df.index[-1])

        if s == 300:
            plt.plot(df.iloc[:, p_index], '.-k', linewidth=3, label=s)
            plt.text(df.index[-1], df.iloc[-1, p_index] - 0.05, s if isinstance(s, str) else db_id_to_name(s),
                     color='gold',
                     fontsize=9, alpha=0.8)
        else:
            plt.plot(df.iloc[:, p_index], '.-', label=s)
            plt.text(df.index[-1], df.iloc[-1, p_index] - 0.05, s if isinstance(s, str) else db_id_to_name(s),
                     color='gray',
                     fontsize=9, alpha=0.8)
        del df

    # plt.legend(stocks)
    # plt.legend(bbox_to_anchor=(1.01,0.5), loc="center left")
    if isinstance(stocks[0], str):
        plt.legend(stocks, bbox_to_anchor=(1.01, 1), loc="upper left")
    else:
        plt.legend([db_id_to_name(s) for s in stocks], bbox_to_anchor=(1.01, 1), loc="upper left")

    plt.grid('on')
    plt.title(title + ' ({})'.format(price_algo))
    # plt.tight_layout()

    save_file = r'{}\tdx_{}_{}_{}.png'.format(savepath, title, ndays, price_algo)
    plt.savefig(save_file, bbox_inches="tight")
    print('save file:', save_file)
    # plt.show()


def test_stock_file():
    conn = sqlite3.connect('stocks.db')
    stocks = conn.execute('''select Name from stocks''').fetchall()

    print(stocks[0])

    index = 0
    for s in stocks:
        index = index + 1
        if index > 300:
            break

        id = db_name_to_id(s[0])
        print(id)
        print(tdx_id_to_klinefile(id))

    # plot_stocks()
    pass


def select_industry_stocks(industry):
    conn = sqlite3.connect('stocks.db')

    ret = conn.execute('''select name,symbol from stockbasic where industry = '{0}' '''.format(industry)).fetchall()

    return [r[1] for r in ret]

    pass


@print_durations()
def plot_industry():
    conn = sqlite3.connect('stocks.db')
    ret = conn.execute('''select distinct industry from stockbasic''').fetchall()
    for r in ret[1:]:
        ind = r[0]
        print(ind)
        if ind is None:
            continue
        stocks = select_industry_stocks(ind)
        plot_stocks(stocks, ndays, ind, r'.\tdx_kline')
        print('plot {} finish'.format(ind))


def read_user_dict():
    dict = {}
    with open('ths_user_category.txt', 'r', encoding='utf8') as f:
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


@print_durations()
def plot_dict():
    stock_lists = read_user_dict()

    for k, v in stock_lists.items():
        plot_stocks(v, ndays, k, r'.\tdx_user_kline')
    pass


@print_durations
def plot_ndays():
    for n in [20, 30, 60, 120]:
        global ndays
        ndays = n
        plot_industry()
        # plot_dict()


import unittest


class TestCase(unittest.TestCase):

    @print_durations
    def plot(self):
        ind = '银行'
        stocks = select_industry_stocks(ind)
        print(stocks)
        plot_stocks(stocks, 20, ind)

    def test_plot_all(self):
        global algo
        for algo in [0, 1, 2, 3]:
            self.plot()


if __name__ == '__main__':
    algo = 3

    plot_ndays()
    pass
