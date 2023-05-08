import requests
import json


def get_eastmoney_json(url):
    # set request origin
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',

        'Origin': 'http://data.eastmoney.com',
        'Referer': 'http://data.eastmoney.com/zjlx/detail.html',

    }
    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def get_dpyt_json(url):
    # set request headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        'Origin': 'https://dapanyuntu.com',
        'Referer': 'https://dapanyuntu.com',

    }
    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def dump_changepct():
    jval = get_dpyt_json('https://api.minli.wang/dpyt/getMapParamDataV2?param=mkt_idx.cur_chng_pct')
    # print(json)

    # dump json to file
    with open('data.json', 'w', encoding='utf') as f:
        # fix json dump utf-8
        json.dump(jval, f, ensure_ascii=False, indent=4)

    data = jval['data']

    print(len(data.keys()))

def dump_marketval():
    jval = get_dpyt_json('https://api.minli.wang/dpyt/getMapData?code=global')
    # print(json)

    # dump json to file
    with open('market.json', 'w', encoding='utf') as f:
        # fix json dump utf-8
        json.dump(jval, f, ensure_ascii=False, indent=4)

    data = jval['data']

    print(len(data.keys()))


if __name__ == '__main__':
    # url = "https://98.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=6000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3,f12,f13,f14&_=1582007856998"
    # json = get_eastmoney_json(url)
    # print(json)
    #
    # json = get_dpyt_json('https://api.minli.wang/dpyt/getMapData?code=global')
    # print(json)

    dump_marketval()

    pass



