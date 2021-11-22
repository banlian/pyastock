import pandas as pd
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


class cfg(object):
    # 通达信日K数据的收盘价索引
    # p_index = 3
    # a_index = 4

    # pickle 索引
    p_index = 5
    a_index = 7
    algo = 3
    savepath = r'.\tdx_kline'

    ndays = 60
    # tdx = 1  pickle = 2
    datasource = 2
    pass


exceptions = []


def init_ex():
    global exfile
    exfile = open('plot_exception.log', 'w')
    printex('init ex')
    pass


def printex(*args):
    print(args, file=exfile)


def save_ex():
    printex('save ex')
    exfile.close()


def get_stock_frame(s):
    if cfg.datasource == 1:
        file = get_tdx_kline_file(s)
        if file is None or not os.path.exists(file):
            print('not found', file)
            return None

        try:
            reader = TdxDailyBarReader()
            df = reader.get_df(file)
            return df.tail(cfg.ndays)
        except:
            printex('read frame error', file)
            return None
            pass
    else:
        try:
            df = get_kdf_from_pkl(s)
            return df.tail(cfg.ndays)
        except:
            printex('read pickle error', s)
            return None
            pass


def calc_ref_frameindex(stocks, stockframes):
    frames = []
    for s in stocks:
        f = stockframes[s]
        if f is not None:
            # f = f.reset_index(drop=True)
            frames.append(f)

    frameindex = []
    for i in range(frames[0].shape[0]):
        data = [f.iloc[i, cfg.p_index] for f in frames]
        p = sum([d for d in data if d is not None])
        frameindex.append(p / len(frames))
        pass

    return frameindex


def skip_stock_filter_by_index(*args):
    '''
    过滤重新计算close后的stock dataframe
    '''
    frame = args[0]
    frameindex = args[1]
    price = frame.iloc[:, cfg.p_index].values
    for i in range(len(price)):
        price[i] = price[i] - frameindex[i]
    pmax = max(price)
    pmin = min(price)
    if pmax - pmin < 15:
        return True
    else:
        return False
    pass


def skip_stock_filter(*args):
    '''
    过滤重新计算close后的stock dataframe
    '''
    frame = args[0]
    price = frame.iloc[:, cfg.p_index]
    pmax = max(price)
    pmin = min(price)
    if pmax - pmin < 30:
        return True
    else:
        return False
    pass


def calc_frame_price(frame):
    """
    重新计算close价格 方便绘制多股对比图形
    """
    if cfg.algo == 1:
        r = base_price_algo(frame)
    elif cfg.algo == 2:
        r = price_percentage_algo(frame, False)
    elif cfg.algo == 3:
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
    prices = frame.iloc[:, cfg.p_index].values
    p0 = prices[0]
    for i in range(len(prices)):
        frame.iloc[i, cfg.p_index] = round((prices[i] - p0) / p0 * 100, 2)
    pass
    return 'raw'


def base_price_algo(frame):
    '''
    convert price into base price percentage
    相对起始价格的涨幅不能很好展示每天的涨幅和波动情况
    不能体现股价高位时的波动 高位波动大 但相对初始价格波动较小
    '''
    prices = frame.iloc[:, cfg.p_index].values
    p0 = prices[0]
    for i in range(len(prices)):
        frame.iloc[i, cfg.p_index] = round((prices[i] - p0) / p0 * 100, 2)
    pass

    return 'baseprice'


def center_of_mass_algo(frame):
    """
    计算股价重心
    """
    prices = frame.iloc[:, cfg.p_index].values
    amount = frame.iloc[:, cfg.a_index].values

    p0 = prices[0]

    percents = []

    # calc center of mass
    for i in range(1, len(prices)):
        amountfactor = amount[i] / amount[i - 1]
        # 防止爆量造成 factor 过大
        # atan 0-1基本线性 收敛于2 需要乘以1/tan(1) = 1.27
        amountfactor = math.atan(amountfactor) * 1.27
        p1 = (prices.iloc[i])
        p0 = (prices.iloc[i - 1])
        percents.append(round((p1 - p0) / p0 * 100 * amountfactor, 2))
    pass

    # assign mass
    for i in range(len(prices)):
        if i > 0:
            frame.iloc[i, cfg.p_index] = sum(percents[:i + 1])
        else:
            frame.iloc[i, cfg.p_index] = 0

    pass


def price_percentage_algo(frame, is_amount):
    '''
    convert price into base price percentage
    涨跌幅相加算法
    无法体现股价实际高低情况 涨幅可体现股价波动  涨幅*成交量因子？低的更低 高的更高
    '''
    prices = frame.iloc[:, cfg.p_index].values
    amount = frame.iloc[:, cfg.a_index].values
    amount = [a / 10000000 for a in amount]

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
            p1 = (prices[i])
            p0 = (prices[i - 1])
            percents.append(round((p1 - p0) / p0 * 100 * amountfactor, 2))
        pass
    else:
        # 计算当日涨跌幅
        for i in range(1, len(prices)):
            p1 = (prices[i])
            p0 = (prices[i - 1])
            percents.append(round((p1 - p0) / p0 * 100, 2))

    for i in range(len(prices)):
        if i > 0:
            frame.iloc[i, cfg.p_index] = sum(percents[:i + 1])
        else:
            frame.iloc[i, cfg.p_index] = 0
    pass

    return 'percentage_amount' if is_amount else 'percentage'


def get_tdx_kline_file(s):
    """
    get tdx day file full path
    """
    if isinstance(s, str):
        temp = s
        s = db_name_to_id(s)
        if s is None:
            printex('get_tdx_kline_file error: not found stock id from db:', temp)
            return None

    if not isinstance(s, int):
        printex('get_tdx_kline_file error: input error', s)
        return None

    if s == 300 or s == 999999:
        file = 'sh{0:0>6d}.day'.format(s)
    elif 600000 <= s < 699999:
        file = 'sh{0}.day'.format(s)
    elif s < 10000 or (399999 > s > 300000):
        file = 'sz{0:0>6d}.day'.format(s)
    else:
        printex('get_tdx_kline_file error: stock over range ', s)
        return None

    if file.find('sh') >= 0:
        return r"C:\new_jyplug\vipdoc\sh\lday\{0}".format(file)
    else:
        return r"C:\new_jyplug\vipdoc\sz\lday\{0}".format(file)


def get_pkl_filename(s):
    '''
    id convert to day file name
    '''
    if s is None:
        printex('get_pkl_filename error:', s)
        return None

    if isinstance(s, str):
        temp = s
        s = db_name_to_id(s)
        if s is None:
            printex('get_pkl_filename error: not found stock id from db:', temp)
            return None

    if not isinstance(s, int):
        printex('get_pkl_filename error: input error', s)
        return None

    if s == 300 or s == 999999:
        return 'sh.{0:0>6d}'.format(s)
    if 600000 <= s < 699999:
        return 'sh.{0}'.format(s)
    if s < 10000 or (399999 > s > 300000):
        return 'sz.{0:0>6d}'.format(s)

    printex('get_pkl_filename error: stock over range ', s)
    return None


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



def get_kdf_from_dayfile(s):
    '''
    获取tdx日线数据
    '''
    file = get_tdx_kline_file(s)
    if file is None or os.path.exists(file):
        print('not found file:', file)
        return None
    reader = TdxDailyBarReader()
    f = reader.get_df(file)
    if f.empty:
        f = None
    return f


def get_kdf_from_pkl(s):
    if not isinstance(s, int):
        printex('get pickle error, stock is not int', s)
        temp = s
        s = db_name_to_id(s)
        if s is None:
            printex('find stock id error', temp)
            return None

    file = r'.\rawdata\{}.pkl'.format(get_pkl_filename(s))
    if not os.path.exists(file):
        printex('find pickel error', s)
        return None

    return pd.read_pickle(file)



@print_durations()
def plot_stocks(stocks, title=''):
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

    stock_legends = []

    # recalc stock frames
    price_algo = ''
    stockframes = {}
    for s in stocks:
        if cfg.datasource == 1:
            file = get_tdx_kline_file(s)
            if file is None or not os.path.exists(file):
                print('not found', file)
                stockframes[s] = None
                continue
            try:
                df = reader.get_df(file)
                df = df.tail(cfg.ndays)
            except:
                stockframes[s] = None
                printex('read frame error', file)
                continue
                pass
        else:
            try:
                df = get_kdf_from_pkl(s)
                df = df.tail(cfg.ndays)
            except:
                stockframes[s] = None
                printex('read pickle error', s)
                continue
                pass
        price_algo = calc_frame_price(df)
        stockframes[s] = df

    # calc frames index
    fi = calc_ref_frameindex(stocks, stockframes)

    # plot stock frames
    for s in stocks:

        df = stockframes[s]
        if df is None:
            continue

        if s != 300 and skip_stock_filter_by_index(df, fi):
            continue
        else:
            stock_legends.append(s)

        if s == 300:
            plt.plot(df.iloc[:, 0].values, df.iloc[:, cfg.p_index].values, '.-k', linewidth=3, label=s)
            plt.text(df.iloc[:, 0].values[-1], df.iloc[-1, cfg.p_index] - 0.05,
                     s if isinstance(s, str) else db_id_to_name(s),
                     color='gold',
                     fontsize=9, alpha=0.8)
            plt.plot(df.iloc[:, 0].values, fi, '.-b', linewidth=3, label=s)
            plt.text(df.iloc[:, 0].values[-1], fi[-1] - 0.05,
                     'index',
                     color='gold',
                     fontsize=9, alpha=0.8)
        else:
            plt.plot(df.iloc[:, 0].values, df.iloc[:, cfg.p_index].values, '.-', label=s)
            plt.text(df.iloc[:, 0].values[-1], df.iloc[-1, cfg.p_index] - 0.05,
                     s if isinstance(s, str) else db_id_to_name(s),
                     color='gray',
                     fontsize=9, alpha=0.8)

        # break
        del df

    # plt.legend(stocks)
    plt.legend(bbox_to_anchor=(1.01, 0.5), loc="center left")
    if isinstance(stocks[0], str):
        plt.legend(stock_legends, bbox_to_anchor=(1.01, 1), loc="upper left")
    else:
        plt.legend([db_id_to_name(s) for s in stock_legends], bbox_to_anchor=(1.01, 1), loc="upper left")

    plt.grid('on')
    plt.title(title + ' ({})'.format(price_algo))
    # plt.tight_layout()

    save_file = r'{}\tdx_{}_{}_{}.png'.format(cfg.savepath, title, cfg.ndays, price_algo)
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
        print(get_tdx_kline_file(id))

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

    index = 1
    end = len(ret) - 1
    for r in ret[1:]:
        ind = r[0]
        print(ind)
        if ind is None:
            continue
        stocks = select_industry_stocks(ind)
        t0 = time.time()
        try:
            plot_stocks(stocks, ind)
        except:
            printex('plot industry error:', ind)
            pass
        span = time.time() - t0
        print('plot {} finish {}s {}/{} - algo {} - ndays {}'.format(ind, span, index, end, cfg.algo, cfg.ndays))
        index = index + 1


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
    cfg.savepath = r'.\tdx_user_kline'
    stock_lists = read_user_dict()

    for k, v in stock_lists.items():
        plot_stocks(v, k)
    pass


@print_durations
def plot_ndays():
    for n in [20, 30, 60, 120]:
        cfg.ndays = n
        plot_industry()
        # plot_dict()


import unittest


class TestCase(unittest.TestCase):

    @classmethod
    def setUp(self) -> None:
        init_ex()
        pass

    @print_durations
    def plot(self):
        cfg.savepath = '.'
        ind = '银行'
        stocks = select_industry_stocks(ind)
        print(stocks)
        plot_stocks(stocks, ind)

    def test_plot_all(self):
        cfg.ndays = 60
        for cfg.algo in [1, 2, 3]:
            self.plot()

    def tearDown(self) -> None:
        save_ex()


if __name__ == '__main__':

    init_ex()
    try:
        # for algo in [1,2,3]:
        #     plot_ndays()
        cfg.savepath = r'.\output_kline'
        cfg.algo = 3
        cfg.ndays = 60
        plot_industry()
    except Exception as ex:
        save_ex()
        raise ex

    pass
