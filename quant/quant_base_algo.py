
from MyTT import *


def macross(df, dayoffset=-1):
    closes = df['close']
    ma0 = MA(closes, 5)
    ma1 = MA(closes, 10)
    c = CROSS(ma0, ma1)
    return c
    pass


from stockbase.stock_reader import *

import unittest

class Test_algo(unittest.TestCase):

    def test_cross(self):
        df = get_kdf_from_pkl(600036)

        c = macross(df)
        print(c[-10:])

        pass