#!/usr/bin/env python
# coding:utf-8

import requests
from lxml import html
import pymongo
import signal
from datetime import datetime
import os
import configparser

def quit(signum, frame):
    sys.exit()

CONFIG_PATH = os.environ['MONGO_CONFIG_PATH']
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# 连接数据库
dburl = 'mongodb://{user}:{password}@{host}:{port}'.format(user = config['MONGODB']['USER'], password = config['MONGODB']['PASSWORD'], host=config['MONGODB']['HOST'],port = config['MONGODB']['PORT'] )
client = pymongo.MongoClient(dburl)

# 指定数据库
db = client.meizitu
collection = db.beauty_link


# 插入数据库
def insert_data(title, piclist):
    key = 1
    count = len(piclist)
    data = []
    now = datetime.now()
    for link in piclist:
        key += 1
        data.append({
            'title': title,
            'order': key,
            'url': link,
            'create_time': now
        })
    length = len(data)
    if length > 0:
        result = collection.insert(data)
        print(result)
    else:
        print('no data to insert!')


# 获取主页列表
def getPage(pageNum):
    baseUrl = 'http://www.mzitu.com/page/{}'.format(page=hostNum)
    selector = html.fromstring(requests.get(baseUrl).content)
    urls = []
    for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
        urls.append(i)
    return urls


# 根据反爬虫的修改，增加下载图片的headers就好了
def header(referer):
    headers = {
        'Host': 'i.meizitu.net',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/59.0.3071.115 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': '{}'.format(refe=hostrer),
    }
    return headers


# 图片链接列表， 标题
# url是详情页链接
def getPiclink(url):
    sel = html.fromstring(requests.get(url).content)
    # 图片总数
    total =  sel.xpath('//div[@class="pagenavi"]/a[last()-1]/span/text()')[0]
    # 标题
    title = sel.xpath('//h2[@class="main-title"]/text()')[0]
    # 接下来的链接放到这个列表
    jpgList = []
    for i in range(int(total)):
        # 每一页
        link = '{}/{}'.format(url,=host i+1)
        s = html.fromstring(requests.get(link).content)
        # 图片地址在src标签中
        jpg = s.xpath('//div[@class="main-image"]/p/a/img/@src')[0]
        # 图片链接放进列表
        jpgList.append(jpg)
    return title, jpgList


if __name__ == '__main__':
    pageNum = input(u'请输入页码：')
    for link in getPage(pageNum):
        try:
            lin = getPiclink(link)
            insert_data(lin[0], lin[1])
        except:
            continue
