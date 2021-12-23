from easytrader import *

import time

from easytrader.clienttrader import ClientTrader


class Trader(object):

    def __init__(self):
        self.user = ClientTrader()
        self.user.enable_type_keys_for_editor()


    def load(self):
        self.user.connect(r'C:\同花顺软件\同花顺\xiadan.exe')
        self.positions = self.get_positions()


    def buy(self, stock, price, amount):
        self.user.buy(stock, price=price, amount=amount)
        pass

    def sell(self, stock, price, amount):
        self.user.sell(stock, price=price, amount=amount)
        pass

    def cancel(self):
        pass

    def get_positions(self):
        return self.user.position

    def get_balance(self):
        return self.user.balance


if __name__ == '__main__':

    t = Trader()

    t.load()

    t.buy('600036', 52, 100)
    i = 0
    while i<2:
        i = i+1
        print('position',t.get_positions())
        print('balance',t.get_balance())
    pass
