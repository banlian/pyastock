import easyquotation


quotation  = easyquotation.use("sina")


data = quotation.stocks(['000001', '162411'])

print(data)

from  Ashare import *

df=get_price('600519.XSHG',frequency='60m',count=6)  #分钟线实时行情，可用'1m','5m','15m','30m','60m'
print('贵州茅台60分钟线\n',df)