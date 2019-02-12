#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests
from lxml import html
import os
from fake_useragent import UserAgent
import urllib3
import re
import pymongo
import time
import random
from datetime import datetime

# 连接数据库
client = pymongo.MongoClient(host='127.0.0.1', port=27017)
# 指定数据库
db = client.bing
# 指定集合
document = db.wallpaper

maxsize = 1


# 查询是否已保存
def search(src):
    result = document.find_one({'src': src})
    return result


# 插入数据库
def insert(info):
    document.insert_one(info)


# 爬取页面
def get_page():
    us = UserAgent()
    headers = {
        'Host': 'bing.ioliu.cn',
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

    baseurl = 'https://bing.ioliu.cn'
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(baseurl, headers=headers)
    if response.status_code == 200:
        selector = html.fromstring(response.content)
        text = selector.xpath('//div[@class="page"]/span/text()')[0]
        total = int(text.split('/')[1])
    for pagesize in range(1, total):
        time.sleep(random.uniform(0, 0.005))
        baseurl = 'https://bing.ioliu.cn?p={pagesize}'.format(pagesize=str(pagesize))
        response = requests.get(baseurl, headers=headers)
        if response.status_code == 200:
            selector = html.fromstring(response.content)
            item_list = selector.xpath('//div[@class="container"]/div[@class="item"]')
            for i_item in item_list:
                src = i_item.xpath('.//img/@src')[0]
                title = i_item.xpath('.//div[@class="description"]/h3/text()')
                calendar = i_item.xpath('.//div[@class="description"]/*[@class="calendar"]/em/text()')
                location = i_item.xpath('.//div[@class="description"]/*[@class="location"]/em/text()')
                view = i_item.xpath('.//div[@class="description"]/*[@class="view"]/em/text()')
                like = i_item.xpath('.//div[@class="options"]/span/@likes')
                download = i_item.xpath('.//div[@class="options"]/a[2]/em/text()')
                # src = re.sub(r'_\d{3,4}x\d{3,4}', '_1920x1080', img)

                result = search(src)
                if result:
                    print('----this img had exists--- ', result['title'])
                else:
                    info = {
                        'src': src,
                        'title': title[0] if len(title) else '',
                        'calendar': calendar[0] if len(calendar) else '',
                        'location': location[0] if len(location) else '',
                        'view': int(view[0] if len(view) else ''),
                        'like': int(like[0] if len(like) else ''),
                        'download': int(download[0] if len(download) else ''),
                        'append_date': datetime.now()
                    }
                    print('-----new info---', info)
                    insert(info)
                    info.clear()


if __name__ == '__main__':
    get_page()
