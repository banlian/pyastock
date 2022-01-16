import pandas as pd

from etrade_track.z_helper import *
from stockbase.stock_db import *

stocks = db_select_tscodes()
print(stocks)

download_rsi_data(['sz000001'], '1w', 104)

c = 'sz000001'
pklfile = f'temp/{c}_1w.pkl'
df = pd.read_pickle(pklfile)
print(df)


