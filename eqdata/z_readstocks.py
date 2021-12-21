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


def read_xlsx_codes(excelfile):
    df = pd.read_excel(excelfile)
    df = df.iloc[:, 0]
    codes = [str(r).lower() for r in df.values if len(str(r)) == 8]

    with open(excelfile[:-4] + 'txt', 'w') as fs:
        for c in codes:
            fs.write('{}\n'.format(c))
    pass

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
        codes = read_xlsx_codes('shortz.xlsx')
        print(codes)

    def test_xls(self):

        df = pd.read_csv('short.xls', encoding='gbk', sep='\t')
        print(df)
        print(df.columns)
        print(df.index)