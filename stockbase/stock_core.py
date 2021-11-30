import datetime


class cfg(object):
    # 通达信日K数据的收盘价索引
    # p_index = 3
    # a_index = 4

    # pickle 索引
    # datetime 作为第0列
    # date,code, open,high,low,close, preclose, vol,amount, adj, turn, status, pctChg, isST
    p_index = 5
    a_index = 7
    algo = 3
    savepath = r'..\tdx_kline'
    enable_filter = False
    ndays = 60
    # tdx = 1  pickle = 2
    datasource = 2
    pass


def get_days(ndays):
    days = []
    for i in range(ndays):
        day = datetime.datetime.today() - datetime.timedelta(days=i)
        days.append(datetime.datetime(day.year, day.month, day.day))
    days.reverse()
    return days

