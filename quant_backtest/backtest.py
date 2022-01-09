from quant.quant_backtrack_base import get_trade_days
from stockbase import *



class BackTest(object):

    def __init__(self):
        self.start_date = '2021-09-01'
        self.stop_date = ''
        self.orders = []
        self.posisions = []
        self.cash = 100e4

        pass


    def run(self):

        tradedays = get_trade_days()





if __name__ == '__main__':

    pass