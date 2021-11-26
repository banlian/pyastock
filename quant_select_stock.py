from quant_backtrack_stocks import quant_plot_stocks
from stock_core import cfg

if __name__ == '__main__':
    cfg.p_index = 5

    # select_stocks_2()

    quant_plot_stocks(r'output_quant/quant_select_stock_price_increase.csv')

    pass
