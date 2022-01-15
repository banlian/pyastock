


from plot_multi_stocks import *

import pandas

cfg.savepath = r'.'
cfg.algo = 2
cfg.datasource = 2
cfg.enable_filter = False
cfg.ndays = 60


df = pandas.read_csv('quant_select_stock_rsi_30_rsi_30_2022-01-14.csv', header=None, skiprows=1, skipfooter=1)

stocks = df.iloc[:,0].tolist()

print(stocks)

stocks = [db_id_to_tscode(s) for s in stocks]
print(stocks)
#
# df = get_kdf_from_pkl('sh000300')
#
# print(df.dtypes)
# df = get_kdf_from_pkl('sh600036')
#
# print(df.dtypes)
#
#
plot_stocks(stocks, 'rsi 30')




