#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import requests
import pymongo
import time
import os
from fake_useragent import UserAgent
import re
# from bs4 import BeautifulSoup

# 连接数据库
client = pymongo.MongoClient(host='127.0.0.1', port=27017)
# 指定数据库
db = client.bing
# 指定集合
document = db.wallpaper


# get url
def get_url():
    info = []
    # for result in document.find().sort('_id', pymongo.DESCENDING).limit(100):
    for result in document.find().sort('_id', pymongo.DESCENDING):
        info.append(result)
    return info


us = UserAgent()


headers = {
        "Host": "h1.ioliu.cn",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        'User-Agent': us.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,la;q=0.7,ko;q=0.6,en;q=0.5",
        # "Cookie": "__jsluid=f7d1765611fbb2cf9ea900538aef4098",
    }


def request_download():
    info = get_url()
    for item in info:
        dirname = '/Users/mhy/Pictures/bing'
        src = re.sub(r'_\d+x\d+', '_1920x1080', item['src'])
        group = src.split(r'/')
        # url_str = re.sub(r'_\d+x\d+', '_1920x1080', group[len(group) - 1])
        url_str = group[len(group) - 1]

        title = re.sub(r'\/', '&', item['title'])  # 有些title里面包含字符/，需要处理掉
        title_str = re.split(r'(\(|\（)', title)[0].strip() + '_'

        filename = title_str + url_str
        fullname = '%s/%s' % (dirname, filename)

        ir = requests.get(src, headers=headers)
        if ir.status_code == 200:
            print('----filename----', filename)
            open(fullname, 'wb').write(ir.content)


def remove_dir():
    dirname = '/Users/mhy/Pictures/bing'
    print ("目录为: %s" % os.listdir(os.getcwd()))

    os.unlink("aa.txt")


if __name__ == '__main__':
    request_download()

