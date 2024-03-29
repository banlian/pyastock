import datetime

import time

import win10toast

from qtrade.etrade_track.z_algo_rsi import *
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


def track_short_rsi(stocks, needupdate=True, logf=None, updatef=None, now: datetime = datetime.datetime.now(), rsithreshold=1.5, rsitrigger=0):
    rsi_threshold = rsithreshold
    rsi_trigger = rsitrigger
    selected = []

    for s in stocks:
        index = stocks.index(s)
        ncode = [s]

        if needupdate:
            download_rsi_data(ncode, '60m', 60)
            #print('update 60m', ncode)
        # hour calc
        file1 = './temp/{}_60m.pkl'.format(s)
        if not os.path.exists(file1):
            print('skip 60m data error', s)
            continue
        df = pd.read_pickle(file1.format(s))
        rsis = get_rsi_price_hour(df)
        rsi = rsis[-1]

        pct, close = get_stock_pct(s)
        close1m = close
        delta = round((close1m - rsi) / close1m * 100, 2)

        # 5m calc
        if now is not None:
            # 每2分钟更新rsi
            if now.minute % 3 == 0 or needupdate:
                download_rsi_data(ncode, '15m')
        file3 = './temp/{}_15m.pkl'.format(s)
        if os.path.exists(file3):
            rsi30m = get_rsi(pd.read_pickle(file3), 10)
        else:
            rsi30m = math.nan

        # 更新grid界面
        if updatef is not None:
            updatef(s, rsi, close1m, delta, close, pct, rsi30m)

        rsi_info = ''
        if rsi_trigger <= delta <= rsi_threshold:
            # 接近rsi触发
            rsi_info = '{} {:>3}  c: {:>7.2f}|{:>7.2f}|{:>5.2f}  ({}/{})'.format(s, db_id_to_name(s).strip(), close1m, rsi, delta, index, len(stocks))
        elif delta < rsi_trigger:
            # rsi触发
            # if close1m <= rsi:
            rsi_info = '{} {:>3}  t: {:>7.2f}|{:>7.2f}|{:>5.2f}  ({}/{})'.format(s, db_id_to_name(s).strip(), close1m, rsi, delta, index, len(stocks))
            # 触发rsi了
            selected.append([rsi_info, s, db_id_to_name(s), rsi, close1m, now])

        # 更新rsi日志
        if len(rsi_info) > 0:
            if logf is not None:
                logf(rsi_info)
            print(rsi_info)

    print('-------rsi trigger--------')
    save_rsi_result('', selected)
    print('-------rsi trigger--------')
    return selected
    pass


def save_rsi_result(file, selected):
    file = '{}_z_wx_rsi_track.csv'.format(file)
    content = ''
    with open(file, 'a+') as fs:
        fs.write('{}\n------------\n'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
        for s in selected:
            line = '{},{}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), s[0])
            fs.write(line)
            print(s[0])
            content = content + line
        fs.write('------------')


class RsiTrack(object):

    def __init__(self):
        self.mode = 1
        self.n = datetime.datetime.now()
        self.loopcount = 0
        self.manual = False
        self.logf = None
        self.updatef = None
        self.stocks = []
        self.forcestop = False

        self.rsi_threshold = 2
        self.rsi_triggr = 0
        pass

    def log(self, log):
        if self.logf is not None:
            self.logf(log)
        else:
            print(log)

    def init(self):
        stocks = read_xlsx_codes('short.xls')
        # if self.mode == 1:
        stocks2 = read_xlsx_codes('shortz.xls')
        stocks2 = [s for s in stocks2 if s not in stocks]
        stocks.extend(stocks2)

        self.stocks = stocks
        self.stocknames = ['{}'.format(db_id_to_name(s)) for s in stocks]
        if self.mode == 0:
            self.n = datetime.datetime(2021, 12, 11, 9, 30, 00)
            pass
        else:
            self.n = datetime.datetime.now()

        self.loopcount = 0

        # 判断是否更新rsi数据
        self.lasthour = self.n.hour - 1

    def updatenow(self):
        if self.mode == 1:
            self.n = datetime.datetime.now()
            print(f'{self.n} rsi threshold: {self.rsi_threshold} rsi trigger:{self.rsi_triggr}')
        else:
            self.n = self.n + datetime.timedelta(0, 1)
            # self.rsi_triggr = self.rsi_triggr + 1
            # self.rsi_threshold = self.rsi_threshold + 1
            print(f'{self.n} rsi threshold: {self.rsi_threshold} rsi trigger:{self.rsi_triggr}')

    def check(self):
        return in_trade_time(self.n) and not self.forcestop
        pass

    def checkifupdatersi(self):
        if self.loopcount == 0 or self.manual:
            return True
        if self.mode == 0:
            return True
        # 9:30 10:30 13:00 14:00 更新rsi价格
        if self.n.hour < 12 and self.n.minute in [29, 30] or self.n.hour > 12 and self.n.minute in [59, 0]:
            return True
        return False

    def run(self):
        # 读取监控股票
        self.log('stocks:' + str(len(self.stocks)))

        # 中午休息
        if in_trade_reset_time(self.n):
            if self.n.minute == 1:
                self.log(f'resting {self.n}')
            else:
                print(f'resting {self.n}')
            time.sleep(30)
            self.updatenow()
            return [], 0
            pass

        # 跟踪rsi触发股票
        self.log(f'trade time {self.n} {self.loopcount} start.........')

        updatersi = self.checkifupdatersi()

        t0 = time.time()
        selected = track_short_rsi(self.stocks, updatersi, self.logf, self.updatef, self.n, self.rsi_threshold, self.rsi_triggr)
        et = time.time() - t0
        self.log(f'track stocks by {et:.2f} seconds')

        # 延迟
        delay = 60 - et
        if delay < 0:
            delay = 1

        self.loopcount = self.loopcount + 1
        self.updatenow()

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
