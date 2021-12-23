import datetime
import math

import pandas as pd
import time

import os
import io
import win10toast

from eqdata.z_algo_rsi import *
from stockbase.stock_db import *

toast = win10toast.ToastNotifier()


def notifywin(stock, ret):
    toast.show_toast(stock, ret, icon_path=None, duration=3, threaded=True)


def in_trade_time(now):
    t = now.time()
    t0 = datetime.time(9, 15, 00)
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


def track_short_rsi(stocks, needupdate=True, file='short', notify=None, updatef=None, datetime: datetime = None):
    rsi_threshold = 1.5

    selected = []

    for s in stocks:
        index = stocks.index(s)
        ncode = [s]
        if needupdate:
            download_rsi_data(ncode, '60m')
            # print('update 60m', ncode)
        if datetime is not None:
            # 每2分钟更新rsi
            if datetime.minute % 2 == 0:
                download_rsi_data(ncode, '5m')

        download_rsi_data(ncode, '1m')

        # hour calc
        file1 = './temp/{}_60m.pkl'.format(s)
        if not os.path.exists(file1):
            print('skip rsi data error', s)
            continue
        df = pd.read_pickle(file1.format(s))

        close = df['close'].values[-1]
        rsi = get_rsi_price_hour(df)[-1]
        rsi = round(rsi, 2)

        # 1m calc
        file2 = './temp/{}_1m.pkl'.format(s)
        if not os.path.exists(file2):
            print('skip 1m data error', s)
            continue
        df1 = pd.read_pickle(file2)
        if not df1.empty:
            close1m = df1['close'].values[-1]
            delta = round((close1m - rsi) / close1m * 100, 2)
            pct, close = get_stock_pct(s)
        else:
            close1m = math.nan
            delta = 0
            pct = 0
            close = math.nan

        # 5m calc
        file3 = './temp/{}_5m.pkl'.format(s)
        if os.path.exists(file3):
            rsi30m = get_rsi(pd.read_pickle(file3), 10)
        else:
            rsi30m = math.nan

        # 更新界面
        if updatef is not None:
            updatef(s, rsi, close1m, delta, close, pct, rsi30m)

        rsi_info = ''
        if 0 <= delta <= rsi_threshold:
            # 接近rsi触发
            rsi_info = '{} {:>3}  c: {:>7.2f}|{:>7.2f}|{:>5.2f}  ({}/{})'.format(s, db_id_to_name(s).strip(), close1m, rsi, delta, index, len(stocks))

            # 更新日志
            if notify is not None:
                notify(rsi_info)
            pass
        elif delta < 0:
            # rsi触发
            if close1m <= rsi:
                rsi_info = '{} {:>3}  t: {:>7.2f}|{:>7.2f}|{:>5.2f}  ({}/{})'.format(s, db_id_to_name(s).strip(), close1m, rsi, delta, index, len(stocks))
                # 触发rsi了
                selected.append((rsi_info, s))
        print(rsi_info)

    print('-------rsi trigger--------')
    save_rsi_result(file, selected)
    print('-------rsi trigger--------')
    return selected
    pass


def save_rsi_result(file, selected):
    file = '{}_rsi_track.csv'.format(file)
    content = ''
    with open(file, 'a+') as fs:
        fs.write('{}\n------------\n'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
        for s in selected:
            line = '{},{}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), s[0])
            fs.write(line)
            print(s[0])
            content = content + line
        fs.write('------------')

    # notify('rsi', content )


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


class RsiTrack(object):

    def __init__(self):
        self.mode = 1
        self.n = datetime.datetime.now()
        self.is_update = True
        self.loopcount = 0
        self.logf = None
        self.stocks = []
        self.forcestop = False
        pass

    def log(self, log):
        if self.logf is not None:
            self.logf(log)
        else:
            print(log)

    def init(self):
        stocks = read_txt_code('short.txt')
        stocks2 = read_txt_code('shortz.txt')
        stocks2 = [s for s in stocks2 if s not in stocks]
        stocks.extend(stocks2)

        self.stocks = stocks
        self.stocknames = ['{}'.format(db_id_to_name(s)) for s in stocks]
        if self.mode == 0:
            self.n = datetime.datetime(2021, 12, 11, 9, 30, 00)
            self.is_update = False
            pass
        else:
            self.n = datetime.datetime.now()
            self.is_update = True

        self.loopcount = 0

        # 判断是否更新rsi数据
        self.lasthour = self.n.hour - 1

    def update(self):
        if self.is_update:
            self.n = datetime.datetime.now()

    def check(self):
        return in_trade_time(self.n) and not self.forcestop
        pass

    def checkifupdatersi(self):
        if self.mode == 0:
            return True
        # 9:30 10:30 13:00 14:00 更新rsi价格
        if self.n.hour < 12 and self.n.minute in [29, 30] or self.n.hour > 12 and self.n.minute in [59, 0]:
            return True
        return False

    def run(self, *args):
        # 读取监控股票
        self.log('stocks:' + str(len(self.stocks)))

        if len(args) > 0:
            updatef = args[0]
        else:
            updatef = None

        # 中午休息
        if in_trade_reset_time(self.n):
            if self.n.minute == 1:
                self.log(f'resting {self.n}')
            else:
                print(f'resting {self.n}')
            time.sleep(30)
            self.update()
            return [], 0
            pass

        # 跟踪rsi触发股票
        self.log(f'trade time {self.n} {self.loopcount} start.........')

        updatersi = self.checkifupdatersi()

        t0 = time.time()
        selected = track_short_rsi(self.stocks, updatersi, 'short', lambda s: self.log(s), updatef, self.n)
        et = time.time() - t0
        self.log(f'track stocks by {et:.2f} seconds')

        # 延迟
        delay = 60 - et
        if delay < 0:
            delay = 1

        self.loopcount = self.loopcount + 1
        self.update()

        self.log(f'trade time {self.n} {self.loopcount} finish.........')

        return selected, delay
        pass


if __name__ == '__main__':

    rt = RsiTrack()
    rt.mode = 0

    rt.init()

    print(rt.stocks.index('sz002475'))
    # while rt.check():
    #     rt.run()
    #
    # print('not in trade time')
    # time.sleep(3)

    pass
