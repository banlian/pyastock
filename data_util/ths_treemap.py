import math
import sqlite3
import time

import pandas as pd

from pylab import mpl

from data_util.helper import read_ths_xlsx_to_df

mpl.rcParams['font.sans-serif'] = ['SimHei']  # ָ��Ĭ������
mpl.rcParams['axes.unicode_minus'] = False  # �������ͼ���Ǹ���'-'��ʾΪ���������


def mapcolor1(v):
    r = v
    if math.isnan(r):
        return '#000000'

    if r < 0:
        c = min(abs(r) / 7 * 205 + 50, 255)
        c = int(c)
        return '#00{:02x}00'.format(c)
    else:
        c = min(abs(r) / 7 * 205 + 50, 255)
        c = int(c)
        return '#{:02x}0000'.format(c)
    pass


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


def process_df():
    df = read_ths_xlsx_to_df('../temp/Table1224.xls')
    df.to_pickle('temp/test.pkl')
    df = pd.read_pickle('temp/test.pkl')

    df = df[['    ����', '����ֵ', '������ҵ', '�Ƿ�']]

    df['����ֵ'] = pd.to_numeric(df['����ֵ'], errors='coerce')
    df['�Ƿ�'] = pd.to_numeric(df['�Ƿ�'], errors='coerce')
    df['����ֵ'] = round(df['����ֵ'] / 1e8, 1)
    df['�Ƿ�'] = round(df['�Ƿ�'] * 100, 1)

    df = df[df['����ֵ'] > 10]

    df['all'] = 'all'
    df['color'] = df['�Ƿ�'].map(mapcolor)

    print(df)


def df_treemap(df):
    import plotly.express as px
    mcolors = mapcolors()
    mcolors['(?)'] = '#999999'

    fig = px.treemap(df,
                     path=['all', '������ҵ', '    ����'],
                     # labels='�Ƿ�',
                     # names='    ����',
                     values='����ֵ',
                     color='color',
                     custom_data=['�Ƿ�'],
                     color_discrete_map=mcolors,
                     hover_data=['�Ƿ�'],
                     )
    fig.update_traces(root_color="lightgray",
                      texttemplate='<b>%{label}</b><br><b>%{value:.2f}</b><br><b>%{customdata[0]:.2f}</b><br>',
                      )
    fig.update_layout(margin=dict(t=1, l=1, r=1, b=1))
    img = fig.to_image('png')
    with open('test.png', 'wb') as fs:
        fs.write(img)
    fig.show()


if __name__ == '__main__':

    df = process_df()

    df_treemap(df)
    pass
