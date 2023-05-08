import datetime
import os.path

import sys;

print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['C:\\Users\\z\\Desktop\\wx_trade', 'C:/Users/z/Desktop/wx_trade'])

from qtrade.etrade_track.z_trade_helper import *
from z_algo_rsi import *


def download_data(c, freq='60m', count=60):
    try:
        df = get_price(c, frequency=freq, count=count)  # 分钟线实时行情，可用'1m','5m','15m','30m','60m'
        # print('{}60分钟线\n'.format(c), df)
        df = df.reset_index()
        df.rename({'': 'date'}, axis=1, inplace=True)
        # print('download', c, ' df', df.shape[0])
        df.to_pickle('./temp/{}_{}.pkl'.format(c, freq))
        # df.to_csv('./temp/{}.csv'.format(c))
        return df
    except Exception as ex:
        os.remove('./temp/{}_{}.pkl'.format(c, freq))
        print('download error', c, ex)
        return pd.DataFrame()
    pass
    pass


class Position(object):
    defalt_pos = 20000

    def __init__(self, s):
        self.stock = s
        # 买入价格
        self.buyprice = 0
        self.sellprice = 0
        # 买入时间
        self.buydate = datetime.datetime(2022, 1, 1, 0, 0, 0)
        self.selldate = datetime.datetime(2022, 1, 1, 0, 0, 0)
        # 最高价格
        self.highprice = 0
        # 回落止盈价格
        self.close1price = 0
        # 止损价格
        self.close0price = 0
        # 买入数量
        self.pos = 0
        # 恐慌价格
        self.rsi = 0

    def __str__(self):
        p = self
        return f'{p.stock},{p.pos:8.0f},{p.rsi:6.2f},{p.buyprice:6.2f},{p.buydate:%Y-%m-%d %H:%M:%S},' + \
               f'{p.sellprice:6.2f},{p.selldate:%Y-%m-%d %H:%M:%S},{p.highprice:6.2f},{p.close1price:6.2f},{p.close0price:6.2f}'


def checkforsell(df1m, pos: Position, now: datetime.datetime = None):
    close = df1m['close'].values[-1]
    high = df1m['high'].values[-1]
    low = df1m['low'].values[-1]

    if pos.buydate is not None:
        dt = now - pos.buydate
        if dt.days < 1:
            return

    if pos.pos > 0:
        if close <= pos.close0price * 1.0001:
            # 判断是否止损
            sellpos = pos.pos
            pos.pos = 0
            pos.selldate = now
            pos.sellprice = round(close, 2)
            print(f'sell {s} at {close:.2f} by {sellpos}')

            sell(s, round(close, 2), sellpos)
            pass
        elif close > pos.buyprice:
            # 是否冲高
            # 更新冲高价格
            if high > pos.highprice * 1.01:
                pos.highprice = high
                pos.close1price = high * 0.985

            # 是否冲高了
            if pos.highprice > pos.buyprice:
                if pos.close1price > pos.buyprice:
                    # 回落价格大于买入价格
                    if close < pos.close1price:
                        sellpos = pos.pos
                        pos.pos = 0
                        pos.selldate = now
                        pos.sellprice = round(close, 2)
                        print(f'close1 {s} at {close:.2f} by {sellpos}')

                        sell(s, round(close, 2), sellpos)
                        pos.pos = 0
                        pass
                else:
                    # 回落价格小于买入价格
                    if close <= pos.buyprice * 1.0005:
                        sellpos = pos.pos
                        pos.pos = 0
                        pos.selldate = now
                        pos.sellprice = round(close, 2)
                        print(f'close0 {s} at {close:.2f} by {sellpos}')

                        sell(s, round(close, 2), sellpos)
                        pass
                    pass
        pass

    pass


def checkforbuy(df1m, s):
    pos = Position(s)
    pklfile = f'./temp/{s}_60m.pkl'
    if not os.path.exists(pklfile):
        print(f'{s} rsi data error: {pklfile} not exists')
        return
    rsi = RSIP(pd.read_pickle(pklfile))[-1]
    close = df1m['close'].values[-1]
    delta = (close - rsi) / close * 100

    # 买入条件
    if -1 < delta < 1 and pos.pos <= 0:
        # 提前挂单
        # 计算手数
        count = pos.defalt_pos // (rsi * 100) * 100
        count = max(count, 100)

        rsi = round(rsi, 2)

        # 更新买入状态
        pos.pos = count
        pos.buyprice = rsi
        pos.buydate = datetime.datetime.now()
        # rsi 触发价格
        pos.rsi = rsi
        # 冲高价格
        pos.highprice = rsi
        # 冲高回落止盈价格
        pos.close1price = rsi
        # 止损价格
        pos.close0price = round(rsi * 0.9695, 2)

        buy(s, round(rsi, 2), count)
        print(f'buy {s} at {rsi:.2f} by {count}')
        return pos
    return None
    pass


def update_rsi_data(s, t):
    if not os.path.exists(f'./temp/{s}_60m.pkl'):
        download_data(s, '60m', 100)

    if t.hour < 12 and t.minute in [30, 31] or t.hour > 12 and t.minute in [0, 1]:
        download_data(s, '60m', 100)
    pass


def get_stocks():
    # codes = read_xlsx_codes('short.xls')
    # codes = read_txt_code('short.txt')
    codes = db_select_tscodes()
    codes = [c for c in codes if 500 < db_select_marketval(int(c[2:])) < 1000]

    return codes
    pass


def buy(s, price, count):
    trader.buy(s, price, count)
    pass


def sell(s, price, count):
    trader.sell(s, price, count)
    pass


def position(s):
    pos = trader.get_positions()
    if s[2:] in pos.keys():
        return pos[s[2:]]
    return [0, 0]
    pass


def loadpositions():
    pos = {}
    with open('positions.csv', 'r') as fs:
        lines = fs.readlines()
        for l in lines:
            l = l.strip('\r\n')
            if len(l) > 0:
                data = l.split(',')
                p = Position(data[0])
                p.stock = data[0]
                p.pos = int(float(data[1]))
                p.rsi = float(data[2])
                p.buyprice = float(data[3])
                p.buydate = datetime.datetime.strptime(data[4], '%Y-%m-%d %H:%M:%S')
                p.sellprice = float(data[5])
                p.selldate = datetime.datetime.strptime(data[6], '%Y-%m-%d %H:%M:%S')
                p.highprice = float(data[7])
                p.close1price = float(data[8])
                p.close0price = float(data[9])
                pos[p.stock] = p
    return pos
    pass


def savepositions(pos: dict[str, Position]):
    with open('positions.csv', 'w') as fs:
        for k, p in pos.items():
            fs.write(f'{p.stock},{p.pos},{p.rsi:.2f},{p.buyprice:.2f},{p.buydate:%Y-%m-%d %H:%M:%S},'
                     f'{p.sellprice:.2f},{p.selldate:%Y-%m-%d %H:%M:%S},{p.highprice:.2f},{p.close1price:.2f},{p.close0price:.2f}\n')
    pass


if __name__ == '__main__':

    stocks = get_stocks()
    print(stocks)

    print('load trader')
    trader = ThsTrader()
    trader.load()

    pos = trader.get_positions()

    print('load positons:')
    positions = loadpositions()

    delpos = []
    for k, p in positions.items():
        if k[2:] not in pos.keys():
            delpos.append(k)
    for k in delpos:
        del positions[k]

    print(positions)
    stocks.extend(positions.keys())

    names = {}
    for s in stocks:
        names[s] = db_id_to_name(s)

    t0 = datetime.time(9, 20, 00)
    t1 = datetime.time(11, 31, 00)
    t2 = datetime.time(12, 59, 00)
    t3 = datetime.time(15, 1, 00)

    i = 0
    while True:
        i = i + 1
        now = datetime.datetime.now()
        print('loop', i, now)

        # 判断交易时间
        if t0 < now.time() < t3:
            if t1 < now.time() < t2:
                print('rest')
                time.sleep(20)
                continue
            pass
        else:
            print('not in trade time')
            break

        st0 = time.time()
        for s in stocks:
            if s[2:5] in ['688'] or s[2:3] =='8':
                print(f'skip {s}')
                continue

            print(f'check {s} {names[s]} {stocks.index(s)}/{len(stocks)}')

            # rsi数据更新
            try:
                update_rsi_data(s, now)

                # 最新价格
                df1m = download_data(s, '1m', 3)

                if s in positions.keys():
                    p = positions[s]
                    if p.pos > 0:
                        print(f'check for sell {s}')
                        # check for sell
                        checkforsell(df1m, p, now)
                        pass
                    # else:
                    #     # check for buy
                    #     checkforbuy(df1m, p)
                    #     pass
                else:
                    if trader.get_avaliable() < Position.defalt_pos:
                        # print('not enough money')
                        continue
                    if len(positions.keys()) > 8:
                        # print('positon full')
                        continue

                    # print(f'check for buy {s}')
                    pos = checkforbuy(df1m, s)
                    if pos is not None:
                        positions[s] = pos
                        print(f'buy success, update pos:{pos}')
            except Exception as ex:
                print('error:', s, ex)
                pass

        et = time.time() - st0
        sleep = max(1.0, 30.0 - et)
        print(f'sleep:{sleep:.2f}')
        time.sleep(sleep)

        savepositions(positions)

    print('exit')

    for i in range(5):
        time.sleep(1)
        print(f'wait {5 - i} s to exit')
