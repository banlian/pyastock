
import time

import easytrader
from easytrader.clienttrader import ClientTrader

user = ClientTrader()
user.enable_type_keys_for_editor()
user.connect(r'C:\同花顺软件\同花顺\xiadan.exe')

for i in range(1):
    print('balance',user.balance)
    print('today_trades',user.today_trades)
    print('position',user.position)
    print('position',user.cancel_entrusts)
    user.buy('002594', price=298, amount=100)
    user.sell('002594', price=299, amount=100)
    print(user.today_trades)
    time.sleep(0.2)
    print(i)
print('exit')

