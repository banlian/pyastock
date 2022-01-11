
#%%
# rsi 连续买卖测试

import datetime
import math

from MyTT import *
from etrade_track.z_algo_rsi import *
from etrade_track.z_helper import *



def getday(dt):
    dt = datetime.datetime.utcfromtimestamp(dt.astype('O') / 1e9)
    # print(dt.day)
    return dt.day
    pass

def format_np_datetime(dt):
    dt = datetime.datetime.utcfromtimestamp(dt.astype('O') / 1e9)
    return dt.isoformat()


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
    hold = 0  #  买入状态
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
        rsip = round(rsi[ri], 2)

        if hold == 0:
            # 买入判断
            # empty wait to buy
            # if low < rsip and rsiv[ri] <= 20:
            if low < rsip:
                close10 = max(df['high'].values[ri - 10:ri])
                delta = (close - close10) / close10 * 100
                if delta > -2 or delta < -6:
                    # 相对前十个小时最高收盘价
                    continue
                    pass
                if enrsi and rsiv[ri] > 20:
                    # 启用 rsi 判断 且 rsi 未触发
                    # 跳过
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
                op.append([1, rsip, date[ri]])
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
                    op.append([-1, sell0p, date[ri]])
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
                # 冲高
                if holdhigh > 0:
                    # 回落止盈价格
                    highp = holdhigh - dcount * hdelta
                    # 高点回落
                    if close < highp:
                        if hold > 0:
                            if highp > holdp:
                                # 回撤至固定点位卖出
                                op.append([0, highp, format_np_datetime(date[ri])])
                                # print(f'sell1:{highp:.2f} {date[ri]}')
                            else:
                                # 回撤至原价卖出
                                op.append([-1, holdp, format_np_datetime(date[ri])])
                                # print(f'sell0:{holdp:.2f} {date[ri]}')
                            selldate = date[ri]
                            hold = -1

            if ri == ei - 1:
                # 最后强制卖出
                if close > holdp:
                    # 止盈
                    op.append([0, close, format_np_datetime(date[ri])])
                    # print(f'sell1:{highp:.2f} {date[ri]}')
                else:
                    # 止损
                    op.append([-1, close, format_np_datetime(date[ri])])
                    # print(f'sell0:{holdp:.2f} {date[ri]}')
                hold = -1
                pass

        if hold == -1:
            # 卖空后 隔日继续判断买入
            if getday(date[ri]) != getday(selldate):
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
    #print(opstr)
    return opstr



def get_codes():
    file = 'table0110'
    df = pd.read_csv('../temp/Table0111.xls', encoding='gbk', sep='\t')
    df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce')
    df['总市值'] = df['总市值'] / 1e8
    df = df[df['总市值'] < 1000]
    df = df[df['总市值'] > 500]

    code = df.iloc[:, 1]
    print(len(code))
    return code

c='sh603486'
download_rsi_data([c], '60m', 4 * 5 * 20)
df = pd.read_pickle(f'temp/{c}_60m.pkl')
ops, pct = rsi_fuck_df_cts(df, si=-4*5*20, ei=0, dcount=6)
for op in ops:
    print(op)
print(pct)
