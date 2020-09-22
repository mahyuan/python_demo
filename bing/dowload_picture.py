#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import requests
import pymongo
import time
import os
from fake_useragent import UserAgent
import re
import random
# from bs4 import BeautifulSoup
import os
import configparser
import platform

CONFIG_PATH = os.environ['MONGO_CONFIG_PATH']

def get_config():
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    return cfg

# 连接数据库
config = get_config()

# 连接数据库
dburl = 'mongodb://{user}:{password}@{host}:{port}'.format(user = config['MONGODB']['USER'], password = config['MONGODB']['PASSWORD'], host=config['MONGODB']['HOST'],port = config['MONGODB']['PORT'] )
client = pymongo.MongoClient(dburl)

# 指定数据库
db = client.bing
# 指定集合
document = db.wallpaper

# get url
def get_url():
    info = []
    # for result in document.find().sort('_id', pymongo.DESCENDING).limit(100):
    for result in document.find({}, {'src': 1, 'title': 1}).sort('_id', pymongo.DESCENDING):
        info.append(result)
    return info


headers = {
        "Host": "h1.ioliu.cn",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        'User-Agent': UserAgent(verify_ssl=False).random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,la;q=0.7,ko;q=0.6,en;q=0.5",
        # "Cookie": "__jsluid=f7d1765611fbb2cf9ea900538aef4098",
    }

def UsePlatform( ):
    sysstr = platform.system()
    print('sysstr', sysstr)
    return sysstr

def request_download():
    info = get_url()
    count = 0

    sysstr = UsePlatform()

    if(sysstr =="Windows"):
        print ("Call Windows tasks")
    elif(sysstr == "Linux"):
        dirname = '/mnt/e/images/bing/bing'
        print ("Call Linux tasks")
    else:
        dirname = '/Users/mhy/Pictures/bing'
        print ("Other System tasks")


    for item in info:
        print('--item-', item)
        suffix = "?imageslim";

        if 'src' in item.keys():
            origin_url = item['src']
            src = re.sub(r'_\d+x\d+', '_1920x1080', origin_url)
            group = src.split(r'/')
            # url_str = re.sub(r'_\d+x\d+', '_1920x1080', group[len(group) - 1])
            url_str = group[len(group) - 1]

            title = re.sub(r'\/', '&', item['title'])  # 有些title里面包含字符/，需要处理掉

            url_str = re.sub(r'\?imageslim', '', url_str) if url_str.endswith(suffix) else url_str

            title_str = re.split(r'(\(|\（)', title)[0].strip() + '_'

            filename = title_str + url_str
            fullname = '%s/%s' % (dirname, filename)

            # 判断文件是否已存在
            is_exists = os.path.isfile(fullname)
            count += 1

            if not is_exists:
                ir = requests.get(src, headers=headers)
                if ir.status_code == 200:
                    print('----download file----', filename)
                    open(fullname, 'wb').write(ir.content)
            else:
                print('path: {}, is_exists: {}, count: {}'.format(fullname, is_exists, count))


# def remove_dir():
#     dirname = '/Users/mhy/Pictures/bing'
#     print ("目录为: %s" % os.listdir(os.getcwd()))

#     os.unlink("aa.txt")


if __name__ == '__main__':
    request_download()
