from Ashare import *
from MyTT import *
from qtrade.etrade_track.z_helper import *
from stockbase.stock_db import *

stocks = db_select_tscodes()
print(stocks)


weekcount = 100


#
# for c in stocks:
#     pklfile = f'./temp/{c}_1w.pkl'
#     if not os.path.exists(pklfile):
#         print(pklfile)
#         download_rsi_data([c], '1w', weekcount)
#         if not os.path.exists(pklfile):
#             print(f'{c} week data error1')
#             break
#             # continue
#         pass
#

# 接近周线恐慌价格

with open('rsi_week.csv', 'w') as fs:
    for c in stocks:
        try:
            # print(stocks.index(c))
            pklfile = f'./temp/{c}_1w.pkl'

            if not os.path.exists(pklfile):
                download_rsi_data([c], '1w', weekcount)
                if not os.path.exists(pklfile):
                    print(f'{c} week data error1')
                    continue
                pass

            if not os.path.exists(pklfile):
                print(f'{c} week data error2')
                continue
            df = pd.read_pickle(pklfile)

            rsi = RSIP(df)
            r = rsi[-1]
            close = df['close'].values[-1]
            delta = round((close - r) / close * 100, 2)

            if delta < 3:
                # 周线接近恐慌
                rsistr = f'{c} {db_id_to_name(c)} {close:.2f} {r:.2f} {delta:.2f}'
                print(rsistr)
                fs.write(rsistr.replace(' ', ',')+'\n')
        except Exception as ex:
            print(c, ex)
            pass
    pass

print('finish')