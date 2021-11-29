from quant_base_factor import factor_ma


def algo_ma_inc(df, date='2021-11-24', dayoffset=0):
    """
    均线多头判断
    """
    if df is None:
        print('frame null')
        return False

    d = df[df['date'] == date]
    dindex = d.index[0] + dayoffset
    if not d.empty and df.index[0] <= dindex <= df.index[-1]:
        df = df[:dindex]

        ma5 = factor_ma(df, 5)
        ma10 = factor_ma(df, 10)
        ma20 = factor_ma(df, 20)
        ma30 = factor_ma(df, 30)
        ma60 = factor_ma(df, 60)

        if ma5 >= ma10 and ma10 >= ma20 and ma20 >= ma30 and ma30 >= ma60:
            # 均线多头
            return True
    # 不选
    return False


def algo_ma_cross(df, date='2021-11-24', dayoffset=0):
    """
    均线多头判断
    """
    if df is None:
        print('frame null')
        return False

    d = df[df['date'] == date]
    dindex = d.index[0] + dayoffset
    if not d.empty and df.index[0] <= dindex <= df.index[-1]:
        df = df[:dindex]

        ma5 = factor_ma(df, 5)
        ma10 = factor_ma(df, 10)
        ma20 = factor_ma(df, 20)
        ma30 = factor_ma(df, 30)
        ma60 = factor_ma(df, 60)

        if ma5 >= ma10 and ma10 >= ma20 and ma20 >= ma30 and ma10 >= ma60 and ma20 < ma60:
            # 均线多头
            return True
    # 不选
    return False
