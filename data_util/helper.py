import pandas as pd


def read_ths_xlsx_to_df(file):
    if file.endswith('xlsx'):
        print('read xlsx')
        df = pd.read_excel(file)
    elif file.endswith('xls'):
        print('read xls')
        df = pd.read_csv(file, encoding='gbk', sep='\t')
        df['涨幅'] = df['涨幅'].str.strip('%')
        df['换手'] = df['换手'].str.strip('%')
    else:
        print('file format error')
        raise ValueError('format')

    print(df.columns)

    df = df[['代码', '    名称', '开盘', '最高', '最低', '现价', '昨收', '总金额', '总市值', '总手', '换手', '涨幅', '所属行业']]

    cols = ['开盘', '最高', '最低', '现价', '昨收', '总金额', '总市值', '总手', '换手', '涨幅', ]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    print(df)
    print(df.columns)
    print(df.dtypes)
    return df


def get_stock_type(stock_code):
    """判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    :return 'sh' or 'sz'"""
    assert type(stock_code) is str, "stock code need str type"
    sh_head = ("50", "51", "60", "90", "110", "113", "132", "204", "5", "6", "9", "7")
    if stock_code.startswith(("sh", "sz", "zz")):
        return stock_code[:2]
    else:
        return "sh" if stock_code.startswith(sh_head) else "sz"
