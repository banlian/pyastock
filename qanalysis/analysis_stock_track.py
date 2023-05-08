from analysis_base import track_to_csv, track_to_plot
from quant.quant_base import read_quant_output_stocks

from stockbase.stock_user_dict import *


def stock_track():
    dict = read_user_dict()
    print(dict.keys())

    plot_days = 60

    if dict['csv'] is not None:
        stocks = dict['csv']
        track_to_csv('csv', stocks, 7)
        track_to_plot('csv', stocks, plot_days)

    if dict['short'] is not None:
        stocks = dict['short']
        track_to_csv('short', stocks, 7)
        track_to_plot('short', stocks, plot_days)


    print('finish')
    pass

def quant_track():

    results = read_quant_output_stocks('quant/quant_select_stock/quant_select_stock.csv')

    track_to_csv('quant', [r[0] for r in results], 2)



if __name__ == '__main__':

    quant_track()
    pass
