
import math
import pandas as pd

from stock_core import *


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
    """
    convert price into base price percentage
    相对起始价格的涨幅不能很好展示每天的涨幅和波动情况
    不能体现股价高位时的波动 高位波动大 但相对初始价格波动较小
    """
    prices = frame.iloc[:, cfg.p_index].values
    p0 = prices[0]
    for i in range(len(prices)):
        frame.iloc[i, cfg.p_index] = round((prices[i] - p0) / p0 * 100, 2)
    pass
    return 'raw'


def base_price_algo(frame):
    """
    convert price into base price percentage
    相对起始价格的涨幅不能很好展示每天的涨幅和波动情况
    不能体现股价高位时的波动 高位波动大 但相对初始价格波动较小
    """
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
    averge = sum(amount) / len(amount)
    amount = [averge if a == 0 else amount for a in amount]
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
    """
    convert price into base price percentage
    涨跌幅相加算法
    无法体现股价实际高低情况 涨幅可体现股价波动  涨幅*成交量因子？低的更低 高的更高
    """
    prices = frame.iloc[:, cfg.p_index].values
    amount = frame.iloc[:, cfg.a_index].values
    amount = [a / 10000000 for a in amount]
    averge = sum(amount) / len(amount)
    amount = [averge if a == 0 else a for a in amount]

    p0 = prices[0]
    # print('base price', p0)

    percents = [0, ]

    if is_amount:
        # 计算当日涨跌幅*成交量因子
        for i in range(1, len(prices)):
            amountfactor = amount[i] / amount[i - 1]
            if math.isnan(amountfactor):
                print(amountfactor)
                pass
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








