import pandas as pd
from funcy import print_durations

import time
import matplotlib.pyplot as plt

from pylab import mpl

from stock_db import *
from stock_index_algo import *
from stock_price_algo import *
from stock_reader import *
from stock_user_dict import read_user_dict

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

width, height = 25, 12.5
plt.rcParams['figure.figsize'] = width, height



@print_durations()
def plot_stocks(stocks, title=''):
    """
    plot multi stocks k line in one figure
    """

    # 强制最后比较沪深300指数
    stocks.append(300)

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

    # re calc stock frames
    algo_name = ''
    dfs = {}

    for s in stocks:
        if cfg.datasource == 1:
            df = get_kdf_from_tdx(s)
        else:
            df = get_kdf_from_pkl(s)

        if df is None or df.empty:
            dfs[s] = None
            printex('read frame error: no stock data', s, cfg.datasource)
            continue

        df = get_df_ndays(df, cfg.ndays)

        algo_name = calc_frame_price(df)
        dfs[s] = df

    days = get_days(cfg.ndays)

    # calc frames index
    dfindex = calc_ref_frameindex(stocks[:-1], dfs, days)

    stocks = [s for s in stocks if s == 300 or not skip_stock_filter_by_index(dfs[s], dfindex)]

    # plot stock frames
    for s in stocks:
        df = dfs[s]
        if df is None:
            continue

        px = df.index

        if s == 300:
            # 300 指数pickle未能正常更新
            plt.plot(px, df.iloc[:, cfg.p_index].values, '.-k', linewidth=3, label=str(s))
            plt.text(px[-1], df.iloc[-1, cfg.p_index] - 0.05,
                     s if isinstance(s, str) else db_id_to_name(s),
                     color='gold',
                     fontsize=9, alpha=0.8)

            # 应该用最新时间索引
            plt.plot(days, dfindex, '.-b', linewidth=3, label='index')
            plt.text(days[-1], dfindex[-1] - 0.05,
                     'index',
                     color='gold',
                     fontsize=9, alpha=0.8)

        else:
            plt.plot(px, df.iloc[:, cfg.p_index].values, '.-', label=str(s))
            plt.text(px[-1], df.iloc[-1, cfg.p_index] - 0.05,
                     s if isinstance(s, str) else db_id_to_name(s),
                     color='gray',
                     fontsize=9, alpha=0.8)

        # break
        del df

    stocks.append('index')
    plt.legend(bbox_to_anchor=(1.01, 0.5), loc="center left")
    if isinstance(stocks[0], str):
        plt.legend(stocks, bbox_to_anchor=(1.01, 1), loc="upper left")
    else:
        plt.legend([db_id_to_name(s) for s in stocks], bbox_to_anchor=(1.01, 1), loc="upper left")

    plt.grid('on')
    plt.title(title + ' ({})'.format(algo_name))
    # plt.tight_layout()

    save_file = r'{}\tdx_{}_{}_{}.png'.format(cfg.savepath, title, cfg.ndays, algo_name)
    plt.savefig(save_file, bbox_inches="tight")
    print('save file:', save_file)
    # plt.show()


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
        cfg.enable_filter = True
        cfg.savepath = '.'
        ind = '家用电器'
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
        cfg.enable_filter = True
        cfg.ndays = 60
        plot_industry()
    except Exception as ex:
        save_ex()
        raise ex

    pass
