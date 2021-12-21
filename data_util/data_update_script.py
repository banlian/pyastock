from data_util.db_util import update_db_marketvalue
from data_util.fetch_data import fetch_index
from data_util.fetch_update_data_by_xlsx import update_temp_pkls
import datetime


def fetch_indexs():
    fetch_index('sh.000001')
    fetch_index('sh.000300')
    pass


if __name__ == '__main__':
    fetch_indexs()

    now = datetime.datetime.now()
    date = now.strftime('%m%d')
    dateindex = now.strftime('%Y-%m-%d')
    file = '../temp/Table{}.xls'.format(date)
    print(file, dateindex)

    # dateindex = '2021-12-16
    # file = '../temp/Table1216.xlsx'

    update_temp_pkls(file, dateindex)

    update_db_marketvalue(file)
    pass
