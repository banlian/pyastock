import sqlite3


def connectdb():
    return sqlite3.connect(r'..\stocks.db')


def db_name_to_id(name):
    """
    find stock id from db name-id dict
    """
    with connectdb() as conn:

        db = conn.execute(
            '''select symbol from STOCKBASIC where NAME = '{0}' '''.format(name))

        res = db.fetchall()

        if len(res) > 0:
            return res[0][0]
        else:
            return None


def db_id_to_industry(id):
    """
    find stock id from db name-id dict
    """
    if isinstance(id, str):
        return id

    with connectdb() as conn:
        db = conn.execute('''select ind2 from STOCKBASIC where symbol = {0} '''.format(id))
        res = db.fetchall()

        if len(res) > 0:
            return res[0][0]
        else:
            return ''


def db_id_to_tscode(id):
    with connectdb() as conn:
        db = conn.execute('''select ts_code from STOCKBASIC where symbol = {} '''.format(id))
        res = db.fetchall()
        if len(res) == 0:
            return ''
        tscode = str.lower(res[0][0])
        return tscode[-2:] + tscode[:6]


def db_id_to_name(id):
    """
    find stock id from db name-id dict
    """
    if isinstance(id, str):
        if id[:2] in ['sh', 'sz']:
            with connectdb() as conn:
                tc = '{}.{}'.format(id[2:], id[:2].upper())
                db = conn.execute('''select name from STOCKBASIC where ts_code = '{0}' '''.format(tc))
                res = db.fetchall()
                if len(res) > 0:
                    return res[0][0]
                else:
                    return str(id)
        return id

    with connectdb() as conn:
        db = conn.execute('''select name from STOCKBASIC where symbol = {0} '''.format(id))
        res = db.fetchall()

        if len(res) > 0:
            return res[0][0]
        else:
            return str(id)


def db_select_stocknames():
    with connectdb() as conn:
        db = conn.execute('''select name from STOCKBASIC''')
        res = db.fetchall()
    return [r[0] for r in res]


def db_select_stockcodes():
    with connectdb() as conn:
        db = conn.execute('''select ts_code from STOCKBASIC''')
        res = db.fetchall()
    return [r[0][:6] for r in res]


def db_select_stockids():
    with connectdb() as conn:
        db = conn.execute('''select symbol from STOCKBASIC where marketvalue>0''')
        res = db.fetchall()
    return [r[0] for r in res]


def db_select_marketval(s):
    with connectdb() as conn:
        db = conn.execute('''select marketvalue from STOCKBASIC where symbol = {} '''.format(s))
        res = db.fetchall()
    return res[0][0] if len(res) > 0 else 0


def db_select_pb(s):
    with connectdb() as conn:
        db = conn.execute('''select pb from STOCKBASIC where symbol = {} '''.format(s))
        res = db.fetchall()
    return res[0][0] if len(res) > 0 else 0


def db_select_pe(s):
    with connectdb() as conn:
        db = conn.execute('''select pe from STOCKBASIC where symbol = {} '''.format(s))
        res = db.fetchall()
    return res[0][0] if len(res) > 0 else 0


def select_industry_stocks(industry):
    with connectdb() as conn:
        ret = conn.execute('''select name,symbol from STOCKBASIC where industry = '{0}' order by marketvalue desc'''.format(industry)).fetchall()

        return [r[1] for r in ret]
    pass


def select_bks():
    with connectdb() as conn:
        db = conn.execute('''select distinct bk from STOCKBASIC where marketvalue>0''')
        res = db.fetchall()
    return [r[0] for r in res]


def select_bk_stocks(bk):
    with connectdb() as conn:
        ret = conn.execute('''select name,symbol from STOCKBASIC where bk = '{0}' order by marketvalue desc'''.format(bk)).fetchall()
        return [r[1] for r in ret]
    pass


import unittest


class Test_db(unittest.TestCase):

    def test_mv(self):
        print(db_select_marketval(600519))

    def test_bks(self):
        bks = select_bks()
        with open('../bk.txt', 'w') as fs:
            for bk in bks:
                fs.write(f'{bk}\n')
        print(bks)
        print(len(bks))

    def test_select_bk_stock(self):
        stocks = select_bk_stocks('白酒')
        print(stocks)
        print([db_id_to_name(s) for s in stocks])
