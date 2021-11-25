import datetime


class cfg(object):
    # 通达信日K数据的收盘价索引
    # p_index = 3
    # a_index = 4

    # pickle 索引
    p_index = 4
    a_index = 6
    algo = 3
    savepath = r'.\tdx_kline'
    enable_filter = False
    ndays = 60
    # tdx = 1  pickle = 2
    datasource = 2
    pass



exceptions = []

exfile = None

def init_ex():
    exceptions = []
    exfile = open('plot_exception.log', 'w')
    printex('init ex')
    pass

def printex(*args):
    print(args, file=exfile)


def save_ex():
    printex('save ex')
    exfile.close()


def get_days(ndays):
    days = []
    for i in range(ndays):
        day = datetime.datetime.today() - datetime.timedelta(days=i)
        days.append(datetime.datetime(day.year, day.month, day.day))
    days.reverse()
    return days

