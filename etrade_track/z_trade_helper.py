from easytrader import *

import time

from easytrader.clienttrader import ClientTrader


class SimTrader(object):
    def __init__(self):
        self.positions = {}
        pass

    def load(self):

        pass

    def buy(self, stock, price, amount):
        print(f'buy {stock} {price} {amount}')
        if stock not in self.positions.keys():
            self.positions[stock] = [price, amount]
        else:
            self.positions[stock][1] = self.positions[stock][1] + amount
        pass

    def sell(self, stock, price, amount):
        print(f'sell {stock} {price} {amount}')
        if stock in self.positions.keys():
            self.positions[stock][1] = self.positions[stock][1] - amount
        else:
            print(f'{stock} not in position')
        pass

    def cancel(self):
        pass

    def get_positions(self):
        return []

    def get_balance(self):
        return 0

    def get_avaliable(self):
        return 5e4

    pass


class ThsTrader(object):

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
        self.user.cancel_all_entrusts()
        pass

    def get_positions(self):
        positions = self.user.position
        pos = {}
        for p in positions:
            pos[p['证券代码']] = [p['实际数量'], p['成本价']]
        return pos

    def get_balance(self):
        return self.user.balance

    def get_avaliable(self):
        return self.get_balance()['可用金额']

if __name__ == '__main__':

    t = ThsTrader()

    t.load()

    i = 0
    while i < 2:
        i = i + 1
        #positions = t.get_positions()
        # print('position', t.get_positions())
        print('balance', t.get_balance())
        print('balance', t.get_avaliable())
    pass
