
#!/usr/bin/env python3
# -* coding: UTF-8 -*-

import requests
from lxml import html
import pymongo
import time
import random
import json
# import ast
from datetime import datetime
import re
# import os
# import sys
# import signal
import urllib3
import user_agent

host = 'https://h5.xiaohongchun.com'

# 连接数据库
# client = pymongo.MongoClient(host='127.0.0.1', port=27017)
client = pymongo.MongoClient(host='121.36.170.117', port=27017) # huaweiyun

# 指定数据库
db = client.xhc
# 指定集合
collname = db.video_comment
# 缺少评论的vid集合
coll_comment = db.v_comment_not_exists

flag = 0


# 获取最后插入的数据
def get_last_vid():
    last = list(collname.find().sort("_id", pymongo.DESCENDING).limit(1))[0]
    return last['video_id']


# 获取最新视频，从数据库查找上video_id最大的，之后的视频就是没有爬到的最新数据
def get_max_vid(order):
    # 获取最新视频，从数据库查找上vid最大的，之后的视频就是没有爬到的最新数据
    # ASCENDING 升序; DESCENDING: 降序
    if order > 0:
        result = list(collname.find().sort('video_id', pymongo.ASCENDING).limit(1))
    else:
        result = list(collname.find().sort('video_id', pymongo.DESCENDING).limit(1))

    if isinstance(result, list):
        return result[0]['video_id']
    else:
        return None


# 写入数据库
def insert_data(info):
    # print('---------data----------- ', info)
    result = collname.insert_many(info)
    print(result)

def getpage(vid):
    ua = user_agent.getua()
    # proxies = {'http': 'http://119.101.125.248', 'https': 'https://119.101.125.226'}
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,la;q=0.7,ko;q=0.6,en;q=0.5",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "upgrade-insecure-requests": "1",
        "method": "GET",
        "scheme": "https",
        "referer":"https://h5.xiaohongchun.com/video?vid={}".format(vid),
        "authority": "h5.xiaohongchun.com",
        "User-Agent": ua,
        "accept-encoding": "br, gzip, deflate"
    }
    baseurl = '{host}/video/{vid}/comments'.format(host=host, vid=vid)

    try:
        # response = requests.get(baseurl, headers=headers, proxies=proxies)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(baseurl, headers=headers, verify=False)
        # print(response)
        if response.status_code == 200:
            selector = html.fromstring(response.content)

            # 分析页面获取数据
            # for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
            pre = selector.xpath('//pre[@vue-data="comments"]/text()')[0]
            info = json.loads(pre)
            return info
    except:
        pass
        return False

# 获取下一个vid
def getNextVid(vid, isIncreasing):
    # print('---isIncreasing---', vid)
    if isIncreasing > 0:
        vid += 1
    else:
        vid -= 1
    return vid

# 持续调用
def start(vid, isIncreasing):
    print('current vid is: ', vid)
    global flag
    while flag < 30:
        res = getpage(vid)
        flag += 1
        if res:
            flag = 0
            print('-------- insert data-----------\n', res)
            insert_data(res)
        elif flag > 20:
            print('-------request failed, flag > 20 ----: ', res)
            break
        else:
            print('-------request failed ----flag: ', flag)


        vid = getNextVid(vid, isIncreasing)
        # time.sleep(random.randint(0,1))
        time.sleep(random.uniform(5, 10))



if __name__ == '__main__':
    # v = int(get_last_vid())
    # order 递增： 1， 递减： 0
    order = 1
    maxVid = get_max_vid(order)
    if isinstance(maxVid, int):
        start(maxVid, order)
    else:
        print('--数据库为空---')
