#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import requests
import pymongo
import time
import os
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

# os.makedirs('./image/', exist_ok=True)




# 连接数据库
client = pymongo.MongoClient(host='127.0.0.1', port=27017)
# 指定数据库
db = client.bing
# 指定集合
document = db.wallpaper


# get url
def get_url():
    info = []
    for result in document.find().sort('_id', pymongo.DESCENDING).limit(100):
        info.append(result)
    return info


us = UserAgent()

headers = {
        'Host': 'h1.ioliu.cn',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'https://bing.ioliu.cn/?p=1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,la;q=0.7,ko;q=0.6,en;q=0.5',
        'User-Agent': us.random,
        'Cookie': 'Hm_lvt_667639aad0d4654c92786a241a486361=1548822638; likes=; Hm_lpvt_667639aad0d4654c92786a241a486361=1548822830'
    }

headers2 = {
        "Host": "h1.ioliu.cn",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        'User-Agent': us.random,
        # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,la;q=0.7,ko;q=0.6,en;q=0.5",
        # "Cookie": "__jsluid=f7d1765611fbb2cf9ea900538aef4098",
    }


def request_download():
    info = get_url()
    for item in info:
        dirname = '/Users/mhy/Pictures/bing'
        src = item['src']
        title = item['title']
        # print(item)
        filename = '%s/%s' % (dirname, src[24:])
        ir = requests.get(src, headers=headers2)
        # print('----r------', ir)
        if ir.status_code == 200:
            open(filename, 'wb').write(ir.content)


def remove_dir():
    dirname = '/Users/mhy/Pictures/bing'
    print ("目录为: %s" % os.listdir(os.getcwd()))

    os.unlink("aa.txt")


if __name__ == '__main__':
    request_download()
