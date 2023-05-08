# %%
# rsi 连续买卖测试

import datetime
import time

from MyTT import *
from qtrade.etrade_track.z_algo_rsi import *
from qtrade.etrade_track.z_helper import *


def getday(dt):
    dt = datetime.datetime.utcfromtimestamp(dt.astype('O') / 1e9)
    deltaday = dt.date() - datetime.date(2021, 1, 1)
    return deltaday.days
    pass


def fdate(dt):
    dt = datetime.datetime.utcfromtimestamp(dt.astype('O') / 1e9)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def rsi_fuck_df_cts(df, si=-20, ei=0, s0pct=3, s1pct=5, enrsi=False, dpct=0.5, dcount=3):
    # 数据准备
    # df 60m数据
    # rsi
    rsiv = RSI(df['close'], 6)
    # rsi 价格
    rsi = RSIP(df)
    # 日期
    date = df['date'].values

    op = []  # 操作记录
    hold = 0  # 买入状态
    holddate = 0  # 买入日期
    holdp = 0  # 买入价格
    hdelta = 0  # 冲高监控最小单位
    holdhigh = 0  # 最高价格

    selldate = 0
    sell0p = 0  # 止损价格
    sell1p = 0  # 止盈价格

    # 回测范围
    rng = range(si, ei, 1)
    for ri in rng:
        low = df['low'].values[ri]
        high = df['high'].values[ri]
        close = df['close'].values[ri]
        open = df['open'].values[ri]
        rsip = round(rsi[ri], 2)

        # print(date[ri], hold)

        if hold == 0:
            # 买入判断
            # empty wait to buy
            # if low < rsip and rsiv[ri] <= 20:
            if low < rsip:
                close10 = max(df['high'].values[ri - 10:ri - 1])
                low10 = min(df['low'].values[ri - 10:ri - 1])
                delta = (low10 - close10) / close10 * 100
                if delta > -2 or delta < -6:
                    # 相对前十个小时最高收盘价
                    print(f'skip delta {fdate(date[ri])} {delta:.2f}')
                    continue
                    pass
                if enrsi and rsiv[ri] > 20:
                    # 启用 rsi 判断 且 rsi 未触发
                    # 跳过
                    print(f'skip rsi {date[ri]} {rsiv[ri]:.2f}')
                    continue
                    pass
                # buy
                hold = 1
                holdp = round(rsip, 2)
                holdhigh = holdp
                hdelta = holdhigh * dpct / 100
                holddate = date[ri]
                sell1p = round(rsip * (100 + s1pct) / 100, 2)
                sell0p = round(rsip * (100 - s0pct) / 100, 2)
                op.append([1, rsip, fdate(date[ri])])
                # print(f'buy:{rsip:.2f} {date[ri]}')
                # print('sell0p', sell0p)
                # print('sell1p', sell1p)

        elif hold > 0 and getday(date[ri]) != getday(holddate):
            # 隔日 卖出判断
            # wait to sell
            if low < sell0p:
                # 股价超过止损线
                # 止损
                if hold > 0:
                    op.append([-1, sell0p, fdate(date[ri])])
                    # print(f'sell0:{sell0p:.2f} {date[ri]}')
                    selldate = date[ri]
                    hold = -1
            elif high > holdp:
                # 冲高回落止盈
                # 股价上涨更新高点
                if high > holdhigh:
                    # 冲高格子计数
                    holdhigh = high
                    hdelta = holdhigh * dpct / 100
                    # print(f'update high:{holdhigh}')
                # 冲高 高点大于成本线
                if holdhigh > holdp:
                    # 回落止盈价格
                    highp = round(holdhigh - dcount * hdelta, 2)
                    # 低点小于回落止盈价格
                    if low < highp and close < open:
                        if hold > 0:
                            if highp > holdp:
                                # 回撤至固定点位卖出
                                op.append([0, highp, fdate(date[ri])])
                                # print(f'sell1:{highp:.2f} {date[ri]}')
                            else:
                                # 回撤至原价卖出
                                op.append([-1, holdp, fdate(date[ri])])
                                # print(f'sell0:{holdp:.2f} {date[ri]}')
                            selldate = date[ri]
                            hold = -1

            if ri == ei - 1:
                # 最后强制卖出
                if close > holdp:
                    # 止盈
                    op.append([0, close, fdate(date[ri])])
                    # print(f'sell1:{highp:.2f} {date[ri]}')
                else:
                    # 止损
                    op.append([-1, close, fdate(date[ri])])
                    # print(f'sell0:{holdp:.2f} {date[ri]}')
                hold = -1
                pass

        if hold == -1:
            # 卖空后 隔日继续判断买入
            if getday(date[ri]) - getday(selldate) > 1:
                # wait next day to continue buy
                hold = 0
            pass

    pcts = [0]
    if len(op) == 2:
        if op[0][0] == 1:
            p0 = op[0][1]
            p1 = op[1][1]
            pct = round((p1 - p0) / p0 * 100, 2)
            pcts = [pct]
    elif len(op) % 2 == 0:
        pcts = []
        for i in range(int(len(op) / 2)):
            p0 = op[i * 2][1]
            p1 = op[i * 2 + 1][1]
            pct = round((p1 - p0) / p0 * 100, 2)
            pcts.append(pct)

    return op, pcts


def formatop(ops):
    if len(ops) == 0:
        return ',,,,,'
    if len(ops) == 1:
        opstr = ','.join([','.join([str(o) for o in op]) for op in ops])
        return opstr + ',,,'

    opstr = ','.join([','.join([str(o) for o in op]) for op in ops])
    # print(opstr)
    return opstr


def get_codes():
    file = 'table0110'
    df = pd.read_csv('../temp/Table0111.xls', encoding='gbk', sep='\t')
    df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce')
    df['总市值'] = df['总市值'] / 1e8
    df = df[df['总市值'] < 30000]
    df = df[df['总市值'] > 10]

    code = df.iloc[:, 1]
    print(len(code))
    return code


def preparedf(c, dflen=320):
    download_rsi_data([c], '60m', dflen)
    df = pd.read_pickle(f'temp/{c}_60m.pkl')
    return df
    pass


def preparedf1(c):
    df = pd.read_pickle(f'temp/{c}_60m.pkl')
    return df
    pass


def preparedfday(c):
    code = f'{c[:2]}.{c[2:]}'
    df = pd.read_pickle(f'../rawdata/{code}.pkl')
    return df


def fuckdf(df):
    df['ma5'] = MA(df['close'], 5)
    df['ma10'] = MA(df['close'], 10)
    df['ma20'] = MA(df['close'], 20)
    df['ma30'] = MA(df['close'], 30)
    df['rsi'] = RSI(df['close'], 6)
    boll = BOLL(df['close'], 20, 2)
    df['bollup'] = boll[0]
    df['bollmid'] = boll[1]
    df['bolldown'] = boll[2]
    return df


def backtest_allstocks():
    dflen = 320

    codes = get_codes().values
    codes = [str.lower(c) for c in codes]
    print(codes)

    tt0 = time.time()

    with open('table0111_backtest_week50.csv', 'w') as fs:
        for c in codes:
            try:
                index = codes.index(c)
                print(index, c, 'start...')
                t0 = time.time()
                df = preparedf(c)

                ssi = df.shape[0]
                print(ssi)
                ops, pct = rsi_fuck_df_cts(df, si=-ssi, ei=0, enrsi=False, dpct=0.5, dcount=3)

                pctsum = sum(pct)
                pct1 = len([p for p in pct if p > 0])
                pct0 = len([p for p in pct if p <= 0])

                fs.write(f'{c},{db_id_to_name(c)},{pctsum:.2f},{pctsum / len(pct):.2f}, {pct1 / len(pct) * 100:.2f},{pct0 / len(pct) * 100:.2f},{len(ops)},{formatop(ops)}\n')

                et = time.time() - t0
                print(index, c, f'finish... {et:.2f}s {index}/{len(codes)}')
            except Exception as ex:
                print(c, ex)

    ett = time.time() - tt0
    print(f'backtest finish {ett:.2f}s')


def backtest_rsi(c):
    t0 = time.time()
    df = preparedf(c, 360)

    fuckdf(df)

    ssi = df.shape[0]
    print(ssi)

    ops, pct = rsi_fuck_df_cts(df, si=-int(ssi / 2), ei=0, enrsi=False, dpct=0.5, dcount=3)

    print(ops)
    print(pct)

    pass


backtest_rsi('sh600036')
