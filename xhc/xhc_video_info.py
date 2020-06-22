#!/usr/bin/env python3
# coding:utf-8

import requests
from lxml import html
import pymongo
import time
import random
from datetime import datetime
import urllib3
import re
from fake_useragent import UserAgent
import os
import configparser
# import sys
# import signal


CONFIG_PATH = os.environ['MONGO_CONFIG_PATH']

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# 连接数据库
dburl = 'mongodb://{user}:{password}@{host}:{port}'.format(user = config['MONGODB']['USER'], password = config['MONGODB']['PASSWORD'], host=config['MONGODB']['HOST'],port = config['MONGODB']['PORT'] )
client = pymongo.MongoClient(dburl)

# 指定数据库
db = client.xhc


# 指定集合
collname = db.video_info
coll_no_exists = db.video_not_exists

flag = 0


# 获取最后插入的数据
def get_last_vid():
    # db.getCollection('video_info').find().sort({vid: 1})
    last = list(collname.find().sort("vid", pymongo.DESCENDING).limit(1))[0]
    return last['vid']


# 获取最新视频，从数据库查找上video_id最大的，之后的视频就是没有爬到的最新数据
def get_limit_vid(order):
    # 获取最新视频，从数据库查找上vid最大的，之后的视频就是没有爬到的最新数据
    # ASCENDING 升序; DESCENDING: 降序
    if order > 0:
        result = list(collname.find().sort('vid', pymongo.DESCENDING).limit(1))
    else:
        result = list(collname.find().sort('vid', pymongo.ASCENDING).limit(1))

    if isinstance(result, list):
        return result[0]['vid']
    else:
        return None


# 根据vid查找数据
def search_byvid(vid):
    result = collname.find_one({'vid': vid}, {'vid': 1})
    return result


# 单条数据写入数据库
def insert_data(info):
    result = collname.insert_one(info)
    return result
    # print('--insert data result----', result)


# 插入多条数据，提高插入性能
def insert_many_data(info):
    result = collname.insert_many(info)
    # print('------result-----', result)
    return result


# 没有请求到的vid存入库
def insert_vid(vid):
    result = coll_no_exists.insert_one({'vid': vid})
    # print('---insert vid result---', result)
    return result

def getpage(vid):
    # proxies = {'http': 'http://119.101.125.248', 'https': 'https://119.101.125.226'}
    headers = {
        "method": "GET",
        "scheme": "https",
        'Connection': 'close',
        # ":path": "/video?vid=346047",
        "authority": "h5.xiaohongchun.com",
        "Referer": "h5.xiaohongchun.com",
        # "cookie": "session_id=6677d9388eca4323a5d241a3424bae91",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "upgrade-insecure-requests": "1",
        "User-Agent":  UserAgent(verify_ssl=False).random,
        "accept-language": "zh-cn",
        "accept-encoding": "br, gzip, deflate"
    }
    baseurl = 'https://h5.xiaohongchun.com/video?vid={}'.format(vid)

    try:
        # response = requests.get(baseurl, headers=headers, proxies=proxies)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(baseurl, headers=headers, verify=False)
        # print(response)
        if response.status_code == 200:
            selector = html.fromstring(response.content)
            # 分析页面获取数据
            # for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
            source = selector.xpath('//div[@id="container"]//video/@src')
            video = source[0] if len(source) > 0 else None
            # print('---source----', t)
            if video:
                type = selector.xpath('//div[@id="container"]//video/@type')
                poster = selector.xpath('//div[@id="container"]//video/@poster')
                avator = selector.xpath('//div[starts-with(@class, "video_user_info")]/div[starts-with(@class, "left-")]//img/@src')
                username = selector.xpath('//div[starts-with(@class, "video_user_info")]/div[starts-with(@class, "middle-")]//a/text()')
                time = selector.xpath('//div[starts-with(@class, "video_detail-")]/div[starts-with(@class, "middle-")]/span/text()')
                totalCount = selector.xpath('//div[starts-with(@class, "video_detail-")]/div[starts-with(@class, "middle-")]/span/text()')
                # 提取播放量中的数字 "1580次播放"
                view_count = int(re.sub(r"\D", "", totalCount[1])) if len(totalCount) else ''
                # title
                title = selector.xpath('//div[starts-with(@class, "video_detail-")]/div[starts-with(@class, "title-")]/text()')
                # 描述
                desc = selector.xpath('//div[starts-with(@class, "vdesc_con-")]/*[starts-with(@class, "desc-")]/text()')
                # 点赞量
                like = selector.xpath('//div[starts-with(@class, "actions-")]/span[starts-with(@class, "like-")]/text()')
                # 收藏量
                collection = selector.xpath('//span[starts-with(@class, "collect-")]/text()')
                # print('title', title)

                collectInt = collection[0] if len(collection) and collection[0] != '收藏' else 0
                # collectInt = int(collection[0]) if len(collection) and collection[0] != '收藏' else 0

                # likeInt = int(like[0]) if len(like) and like[0] != '喜欢' else 0
                likeInt = like[0] if len(like) and like[0] != '喜欢' else 0

                # 数据组装成字典
                info = {
                    # title[0] if len(title) else ''
                    'vid': vid,
                    'src': video,
                    'type': type[0] if len(type) else '',
                    'avator': avator[0] if len(avator) else '',
                    'poster': poster[0] if len(poster) else '',
                    'nick': username[0] if len(username) else '',
                    'upload_time': time[0] if len(time) else '',
                    'view_count': view_count,
                    'title': title[0] if len(title) else '',
                    'desc': desc[0] if len(desc) else '',
                    'like': likeInt,
                    'collection': collectInt,
                    'create_time': datetime.now()
                }
                return info
    except KeyboardInterrupt:
        return False


# 获取下一个vid
def getNextVid(vid, isIncreasing):
    if isIncreasing > 0:
        vid += 1
    else:
        vid -= 1
    return vid


# 持续调用
def start(vid, isIncreasing):
    print('current vid is: ', vid)
    li = []
    videoid = vid
    global flag
    while flag < 100:
        try:
            dbData = search_byvid(videoid)
            if dbData is None:
                res = getpage(videoid)
                print('---res---', res)
                if res:
                    flag = 0
                    li.append(res)
                    if len(li) > 20:
                        insert_many_data(li)
                        li.clear()
                else:
                    flag += 1
                    if flag > 200:
                        if len(li) > 0:
                            insert_many_data(li)
                            li.clear()
                            print('----没有数据了----')
                            break
                time.sleep(random.uniform(2,5))
                videoid = getNextVid(videoid, isIncreasing)
            else:
                print('---db has this vidoe info--', dbData)
                time.sleep(random.uniform(0, 0.5))
                videoid = getNextVid(videoid, isIncreasing)


        except KeyboardInterrupt:
            insert_many_data(li)
            li.clear()
            pass


if __name__ == '__main__':
    # v = int(get_last_vid())
    # 最大：1, 最小： 0
    order = 1
    maxVid = get_limit_vid(order)
    print('---start at---', maxVid)
    if isinstance(maxVid, int):
        vid = maxVid - 1
        # order 递增： 1， 递减： 0
        start(vid, order)

    else:
        print('--数据库为空---')
