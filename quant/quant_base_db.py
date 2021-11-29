from stockbase.stock_db import *


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


import unittest
class Test_db(unittest.TestCase):


    def test_mv(self):
        print(marketvalue(600036))
