import datetime

import time

import os

import win10toast

from eqdata.z_helper import *
from quant_select_stock.algo3_rsi import UserRsiPriceAlgo
from stockbase.stock_db import *

toast = win10toast.ToastNotifier()


def notify(stock, ret):
    toast.show_toast(stock, ret,
                     icon_path=None,
                     duration=3,
                     threaded=True)


def in_trade_time(now):
    t = now.time()
    t0 = datetime.time(9, 25, 00)
    t3 = datetime.time(15, 00, 00)
    if t0 <= t <= t3:
        return True
    return False


def in_trade_reset_time(now):
    t = now.time()
    t1 = datetime.time(11, 30, 00)
    t2 = datetime.time(13, 00, 00)
    if t1 < t < t2:
        return True
    return False
    pass


def track_short_rsi(stocks, needupdate=True, file='short'):
    algo = UserRsiPriceAlgo()
    algo.mode = 0
    algo.rsi_threshold = 1.5

    selected = []

    index = 0
    for s in stocks:
        index = stocks.index(s)
        ncode = [normalize_code(s)]
        if needupdate:
            download_rsi_data_60m(ncode)
            # print('update 60m', ncode)
        download_rsi_data_1m(ncode)

        file1 = './temp/{}.pkl'.format(s)
        if not os.path.exists(file1):
            continue
        df = pd.read_pickle(file1.format(s))

        file2 = './temp/{}_1m.pkl'.format(s)
        if not os.path.exists(file2):
            continue
        df1 = pd.read_pickle(file2)

        if algo.run(df, int(s), -1):
            if not df1.empty:
                # p = df1['low'].values[-1]
                # sret = (s, algo.ret, algo.rsi, p)
                # selected.append(sret)
                pass
            pass

        if algo.closetorsi:
            if not df1.empty:
                p = df1['close'].values[-1]

                if p <= algo.rsi:
                    delta = round((p - algo.rsi) / algo.rsi * 100, 2)
                    rsi_info = '{}\t{:>3}  t: {:>7.2f}|{:>7.2f}|{:>5.2f}  ({}/{})'.format(s, db_id_to_name(int(s)).strip(), p, round(algo.rsi, 2), delta, index, len(stocks))
                    selected.append(rsi_info)
                    print(rsi_info.format(chr(12288)))
                    pass
                else:
                    delta = round((p - algo.rsi) / algo.rsi * 100, 2)
                    if delta > 0:
                        print('{0}\t{1:>3}  c: {2:>7.2f}|{3:>7.2f}|{4:>5.2f}  ({5}/{6})'.format(s, db_id_to_name(int(s)).strip(), p, round(algo.rsi, 2), delta, index, len(stocks)))

    print('-------rsi trigger--------{}'.format(n))
    file = '{}_rsi_track.csv'.format(file)
    content = ''
    with open(file, 'a+') as fs:
        fs.write('{}\n------------\n'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
        for s in selected:
            line = '{},{}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), s)
            fs.write(line)
            print(s)
            content = content + line
        fs.write('------------')

    # notify('rsi', content )

    return selected
    pass


#
# import unittest
#
#
# class Test_Rsi(unittest.TestCase):
#
#     def test_time(self):
#         now = datetime.datetime.now()
#
#         t0 = datetime.time(9, 30, 00)
#         t1 = datetime.time(11, 30, 00)
#         t4 = datetime.time(13, 00, 00)
#         t5 = datetime.time(15, 00, 00)
#
#         print(now.time())


if __name__ == '__main__':

    n = datetime.datetime(2021, 12, 11, 9, 35, 00)
    is_update = False

    # n = datetime.datetime.now()
    # is_update = True

    print(n)


    # 模拟测试用
    def update():
        if is_update:
            global n
            n = datetime.datetime.now()


    index = 0

    # 读取监控股票
    stocks = read_txt_code('short.txt')
    stocks2 = read_txt_code('shortz.txt')
    stocks.extend(stocks2)
    print(stocks)

    # 判断是否更新rsi数据
    lasthour = n.hour - 1

    while in_trade_time(n):
        # 中午休息
        if in_trade_reset_time(n):
            print('resting', n)
            time.sleep(30)
            update()
            continue
            pass

        # 跟踪rsi触发股票
        print('trade time', n, index, 'start.........')

        needupdate = False
        if lasthour != n.hour:
            needupdate = True
            lasthour = n.hour

        t0 = time.time()
        selected = track_short_rsi(stocks, needupdate)
        et = time.time() - t0
        print('track stocks by {:.2f} seconds'.format(et))

        # 延迟
        delay = 60 - et
        if delay < 0:
            delay = 1
        time.sleep(delay)

        index = index + 1
        update()
        print('trade time', n, index, 'finish...........')
        pass

    print('not in trade time')
    time.sleep(3)

    pass
