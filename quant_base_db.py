from stock_db import db_select_stocks, db_select_stockids, db_select_marketval


def all_stocks():
    return db_select_stocks()


def all_stocksid():
    return db_select_stockids()


def stocksource_hs300():
    pass


def stocksource_zz500():
    pass


def stocksource_bk(bkname):
    pass


def stocksource_industry():
    pass


def marketvalue(s):
    """
    市值
    """
    return db_select_marketval(s)
    pass


