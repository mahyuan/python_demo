#!/usr/bin/python
# coding:utf-8

import requests
from lxml import html
import pymongo
import time
import random
from datetime import datetime
import re
# import os
# import sys
# import signal
import urllib3

host = 'https://h5.xiaohongchun.com'

# 连接数据库
client = pymongo.MongoClient(host='127.0.0.1', port=27017)
# 指定数据库
db = client.xhc
# 指定集合
collname = db.video_info
coll_no_exists = db.video_not_exists

# 获取最后插入的数据
def get_last_vid():
    # db.getCollection('video_info').find().sort({vid: 1})
    last = list(collname.find().sort("_id", pymongo.DESCENDING).limit(1))[0]
    return last['vid']


# 根据vid查找数据
def search_byvid(vid):
    result = collname.find_one({'vid': vid}, {'vid': 1})
    return result



# 写入数据库
def insert_data(info):
    result = collname.insert_one(info)
    print('--insert data result----', result)


# 插入多条数据，提高插入性能
def insert_many_data(info):
    result = collname.insert_many(info)
    print('------result-----', result)

# 没有请求到的vid存入库
def insert_vid(vid):
    result = coll_no_exists.insert_one({'vid': vid})
    print('---insert vid result---', result)

# 获取随机手机 user_agents
def get_user_agent():
    user_agents = [
        "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone 6s; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 MQQBrowser/8.3.0 Mobile/15B87 Safari/604.1 MttCustomUA/2 QBWebViewType/1 WKType/1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko Version/12.0 ,Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B411 Safari/600.1.4",
        "Mozilla/5.0 (iPad; CPU OS 6_0_1 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A523 Safari/8536.25",
        "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-CN; EML-AL00 Build/HUAWEIEML-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/11.9.4.974 UWS/2.13.1.48 Mobile Safari/537.36 AliApp(DingTalk/4.5.11) com.alibaba.android.rimet/10487439 Channel/227200 language/zh-CN",
        "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-CN; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/11.9.4.974 UWS/2.13.1.48 Mobile Safari/537.36 AliApp(DingTalk/4.5.11) com.alibaba.android.rimet/10487439 Channel/227200 language/zh-CN",
        "Mozilla/5.0 (Linux; U; Android 8.0.0; zh-CN; VTR-AL00 Build/HUAWEIVTR-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.1.4.994 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_HK",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15G77 wxwork/2.5.1 MicroMessenger/6.3.22 Language/zh",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Mobile/14D27 MicroMessenger/6.7.3(0x16070321) NetType/4G Language/zh_CN",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153 MicroMessenger/6.7.3(0x16070321) NetType/4G Language/zh_CN",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_4 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G35 QQ/6.5.3.410 V1_IPH_SQ_6.5.3_1_APP_A Pixel/750 Core/UIWebView NetType/2G Mem/117"
    ]
    user_agent = random.choice(user_agents)
    return user_agent


def getpage(vid):
    proxies = {'http': 'http://119.101.125.248', 'https': 'https://119.101.125.226'}
    headers = {
        "method": "GET",
        "scheme": "https",
        # ":path": "/video?vid=346047",
        "authority": "h5.xiaohongchun.com",
        # "cookie": "session_id=6677d9388eca4323a5d241a3424bae91",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "upgrade-insecure-requests": "1",
        "User-Agent": get_user_agent(),
        "accept-language": "zh-cn",
        "accept-encoding": "br, gzip, deflate"
    }
    baseurl = '{host}/video?vid={vid}'.format(host=host, vid=vid)

    try:
        # response = requests.get(baseurl, headers=headers, proxies=proxies)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(baseurl, headers=headers, verify=False)
        # print(response)
        if response.status_code == 200:
            selector = html.fromstring(response.content)


        # 分析页面获取数据
        # for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
        video = selector.xpath('//div[@id="container"]//video/@src')[0]
        type = selector.xpath('//div[@id="container"]//video/@type')[0]
        poster = selector.xpath('//div[@id="container"]//video/@poster')[0]
        avator = selector.xpath('//div[starts-with(@class, "video_user_info")]/div[starts-with(@class, "left-")]//img/@src')[0]
        username = selector.xpath('//div[starts-with(@class, "video_user_info")]/div[starts-with(@class, "middle-")]//a/text()')[0]
        time = selector.xpath('//div[starts-with(@class, "video_detail-")]/div[starts-with(@class, "middle-")]/span/text()')[0]
        totalCount = selector.xpath('//div[starts-with(@class, "video_detail-")]/div[starts-with(@class, "middle-")]/span/text()')[1]
        # 提取播放量中的数字 "1580次播放"
        view_count = int(re.sub("\D", "", totalCount))
        # title
        title = selector.xpath('//div[starts-with(@class, "video_detail-")]/div[starts-with(@class, "title-")]/text()')[0]
        # 描述
        desc = selector.xpath('//div[starts-with(@class, "vdesc_con-")]/*[starts-with(@class, "desc-")]/text()')[0]
        # 点赞量
        like = selector.xpath('//div[starts-with(@class, "actions-")]/span[starts-with(@class, "like-")]/text()')[0]
        # 收藏量
        # collection = selector.xpath('//div[starts-with(@class, "actions-")]/span[starts-with(@class, "collect-")]/text()')[0]
        collection = selector.xpath('//span[starts-with(@class, "collect-")]/text()')[0]
        # print('title', title)


        # 数据组装成字典
        info = {
            'vid': vid,
            'src': video,
            'type': type,
            'avator': avator,
            'poster': poster,
            'nick': username,
            'upload_time': time,
            'view_count': view_count,
            'title': title,
            'desc': desc,
            'like': like,
            'collection': collection,
            'create_time': datetime.now()
        }
        return info
    except:
        return False



# 持续调用
def start(vid):
    # 目测视频Id是大于4位的数字
    # vid = 342906
    li = []
    while 1:
        # 160220
        res = getpage(vid)
        # print(type(res))
        vid -= 1
        # 243792
        # 160072
        # if vid < 150000:
        #     print('======ended======')
        #     break

        if res:
            li.append(res)
            if len(li) > 100:
                print('---------data--------', li)
                insert_many_data(li)
                li.clear()
                # time.sleep(random.uniform(0, 0.1))
            else:
                # print('--------<--------')
                pass
        else:
            # print('-------res----:', res)
            pass
        # print('curent vid is: ', vid)
        # time.sleep(random.randint(0, 1))
        time.sleep(random.uniform(0, 0.005))


# 依次查询没有的数据
def loop():
    min_val, max_val = 12877, 345954
    key = max_val
    while key > min_val:
        # 查询数据库，不存在的就请求，请求失败把vid存入vid表，存在的数据插入video表
        data = search_byvid(key)
        # print('vid: {vid}, data: {data}'.format(vid=key, data=data))
        if data:
            print('---db has data----:', data)
        else:
            time.sleep(0.0001)
            res = getpage(key)
            print('---res from request---', res)
            if res:
                # print('---res from exits---', res)
                insert_data(res)
            else:
                # print('---res form page not exists----', res)
                insert_vid(key)

        key -= 1
        print('---------------------------------------------on loop end------vid---------------------', key)


if __name__ == '__main__':
    # v = int(get_last_vid())
    # start(v)
    loop()
