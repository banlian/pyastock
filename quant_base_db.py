from stock_db import db_select_stocks, db_select_stockids, db_select_marketval


def all_stocks():
    return db_select_stocks()


def all_stocksid():
    return db_select_stockids()


def marketvalue(s):
    """
    市值
    """
    return db_select_marketval(s)
    pass


def turn(df, date=''):
    """
    换手率
    """
    v = df.loc[df['date'] == date, 'turn']
    if v.empty:
        return 0
    try:
        return float(v.values[0])
        pass
    except:
        return 0