
import math
import sqlite3
import time

import pandas as pd

from pylab import mpl

from data_util.helper import read_ths_xlsx_to_df

mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题



def mapcolor(v):
    # v = v * 100
    rg = [-4, -3, -2, -1, -0.5, -0.05, 0.05, 0.5, 1, 2, 3, 4]
    colors = ['#00d641', '#1aa448', '#0e6f2f', '#085421', '#083721', '#082221', '#424453', '#4d1414', '#6d1414', '#961010', '#be0808', '#e41414']

    for r in rg:
        if v < r:
            return colors[rg.index(r)]
    return colors[-1]


def mapcolors():
    # colors = ['#00d641', '#1aa448', '#0e6f2f', '#085421', '#424453', '#6d1414', '#961010', '#be0808', '#e41414']
    colors = ['#00d641', '#1aa448', '#0e6f2f', '#085421', '#083721', '#082221', '#424453', '#4d1414', '#6d1414', '#961010', '#be0808', '#e41414']

    ret = {}
    for c in colors:
        ret[c] = c
    return ret
    pass


df = pd.read_csv('../temp/Table0118.xls', encoding='gbk', sep='\t')
df['涨幅'] = df['涨幅'].str.strip('%')
df['换手'] = df['换手'].str.strip('%')
df['5日涨幅'] = df['5日涨幅'].str.strip('%')
df['10日涨幅'] = df['10日涨幅'].str.strip('%')

df.to_pickle('temp/test.pkl')
#df = pd.read_pickle('temp/test.pkl')

df = df[['    名称', '总市值', '所属行业', '涨幅', '5日涨幅']]

df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce')
df['涨幅'] = pd.to_numeric(df['涨幅'], errors='coerce')
df['5日涨幅'] = pd.to_numeric(df['5日涨幅'], errors='coerce')
df['总市值'] = round(df['总市值'] / 1e8, 1)
df['涨幅'] = round(df['5日涨幅'], 1)



#%%

df = df[df['总市值'] > 1]

df['all'] = 'all'
df['color'] = df['涨幅'].map(mapcolor)

print(df)

import plotly.express as px
mcolors = mapcolors()
mcolors['(?)'] = '#999999'

fig = px.treemap(df,
                 path=['all', '所属行业', '    名称'],
                 # labels='涨幅',
                 # names='    名称',
                 values='总市值',
                 color='color',
                 custom_data=['涨幅'],
                 color_discrete_map=mcolors,
                 hover_data=['涨幅'],
                 )
fig.update_traces(root_color="lightgray",
                  texttemplate='<b>%{label}</b><br><b>%{value:.2f}</b><br><b>%{customdata[0]:.2f}</b><br>',
                  )
fig.update_layout(margin=dict(t=1, l=1, r=1, b=1))
img = fig.to_image('png')
with open('temp/test.png', 'wb') as fs:
    fs.write(img)
fig.show()