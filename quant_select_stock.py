from quant_backtrack_select_stocks import quant_plot_stocks
from quant_select_stock_base import *
from stock_core import cfg


def select_max_percent():
    """
    查看最近涨的好的股票
    """
    c0 = MaxPercent()
    c0.max_percent = 50
    c0.days = 30
    quant_run_select_stocks([c0], 0, 'maxpercent')

def select_algo1():
    """
    低位突破
    """
    pass


def select_algo1():
    """
    高位回踩
    """
    pass


def test():
    cfg.p_index = 5

    # select_stocks_2()

    quant_plot_stocks(r'output_quant/quant_select_stock_price_increase.csv')


if __name__ == '__main__':
    select_max_percent()
    pass
