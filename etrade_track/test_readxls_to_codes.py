

import time

import pandas as pd

from etrade_track.z_helper import read_xlsx_codes

#
codes0 = read_xlsx_codes('short.xls')
print(codes0)

#%%

codes1 = read_xlsx_codes('shortz.xls')
print(codes1)
