#!/usr/bin/env python3
# coding:utf-8

import requests
import re
from lxml import html
import pymongo
import random
from datetime import datetime
import urllib3
import time
from fake_useragent import UserAgent
import os
import configparser


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

db = client.xhc

video_collection = db.video_info
video_notexists_collection = db.video_not_exists


# 获取最新的一个不存在记录
def get_next_vid():
    last = list(video_notexists_collection.find().sort("vid", pymongo.DESCENDING).limit(1))[0]
    if 'vid' in last:
        return last
    else:
        return None


# 删除不存在记录
def remove_not_exists_vid(vid):
    res = video_notexists_collection.delete_many({'vid': vid})
    print('---delete vid is-----:', vid)
    return res


# 写入数据库
def insert_data(info):
    result = video_collection.insert_one(info)
    print('--insert data result----', result)


def start():
    try:
        while True:
            result = get_next_vid()

            if 'vid' in result:
                vid = result['vid']
                print('----vid----', vid)
                info = getpage(vid)
                if info:
                    insert_data(info)
                else:
                    print('----info not exists---', info)
                remove_not_exists_vid(vid)
            else:
                print('------没有数据了--------')
                break
            time.sleep(random.uniform(5, 15))
    except KeyboardInterrupt:
        return False



def getpage(vid):
    # proxies = {'http': 'http://119.101.125.248', 'https': 'https://119.101.125.226'}
    headers = {
        "method": "GET",
        "scheme": "https",
        # ":path": "/video?vid=346047",
        "authority": "h5.xiaohongchun.com",
        # "cookie": "session_id=6677d9388eca4323a5d241a3424bae91",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "upgrade-insecure-requests": "1",
        "User-Agent": UserAgent(verify_ssl=False).random,
        "accept-language": "zh-cn",
        "accept-encoding": "br, gzip, deflate"
    }
    baseurl = 'https://h5.xiaohongchun.com/video?vid={vid}'.format(vid=vid)

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
                view_count = int(re.sub("\D", "", totalCount[1])) if len(totalCount) else ''
                # title
                title = selector.xpath('//div[starts-with(@class, "video_detail-")]/div[starts-with(@class, "title-")]/text()')
                # 描述
                desc = selector.xpath('//div[starts-with(@class, "vdesc_con-")]/*[starts-with(@class, "desc-")]/text()')
                # 点赞量
                like = selector.xpath('//div[starts-with(@class, "actions-")]/span[starts-with(@class, "like-")]/text()')
                # 收藏量
                collection = selector.xpath('//span[starts-with(@class, "collect-")]/text()')
                # print('title', title)

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
                    'like': like[0] if len(like) else '',
                    'collection': collection[0] if len(collection) else '',
                    'create_time': datetime.now()
                }
                return info
    except KeyboardInterrupt:
        return False


if __name__ == '__main__':
    start()

