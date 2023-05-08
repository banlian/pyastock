from qtrade.etrade_track.z_helper import read_txt_code
from qtrade.etrade_track.z_track_rsi import track_short_rsi


if __name__ == '__main__':

    # stocks = db_select_stockcodes()

    stocks = read_txt_code('short.txt')
    stocks2 = read_txt_code('shortz.txt')
    stocks.extend(stocks2)

    track_short_rsi(stocks, True)

    pass