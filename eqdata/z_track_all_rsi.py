from eqdata.z_readstocks import read_txt_code
from eqdata.z_track_rsi import track_short_rsi
from stockbase.stock_db import *


if __name__ == '__main__':

    # stocks = db_select_stockcodes()

    stocks = read_txt_code('short.txt')
    stocks2 = read_txt_code('shortz.txt')
    stocks.extend(stocks2)

    track_short_rsi(stocks, True, 'all')

    pass