import pandas as pd

from eqdata.z_helper import *


def read_codes_nomalized():
    with open('short.txt', 'r', encoding='utf-8') as fs:
        lines = fs.readlines()
        lines = [l.strip('\r\n ') for l in lines]
        lines = [l for l in lines if len(l) > 0]
    return [normalize_code(c) for c in lines]


def read_txt_code(file):
    with open(file, 'r', encoding='utf-8') as fs:
        lines = fs.readlines()
        lines = [l.strip('\r\n ') for l in lines]
        lines = [l for l in lines if len(l) > 0]
    return lines


def read_xlsx_codes(excelfile='short.xlsx'):
    df = pd.read_excel(excelfile)
    df = df.iloc[:, 0]
    codes = [str(r)[2:] for r in df.iloc[:].values if len(r) == 8]
    return codes


import unittest


class Test_Data(unittest.TestCase):

    def test_read_code(self):
        codes = read_txt_code()
        print(codes)

    def test_read_xlsx_code(self):
        df = pd.read_excel('short.xlsx')

        df = df['代码']
        df.reset_index()
        df.to_csv('short.pkl')

    def test_read_pkl_codes(self):
        codes = read_xlsx_codes('short.xlsx')
        print(codes)

        with open('short.txt', 'w') as fs:
            for c in codes:
                fs.write('{}\n'.format(c))

        pass

    def test_read_pkl_codes2(self):
        codes = read_xlsx_codes('shortz.xlsx')
        print(codes)

        with open('shortz.txt', 'w') as fs:
            for c in codes:
                fs.write('{}\n'.format(c))

        pass
