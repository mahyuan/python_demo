#!/usr/bin/python
# coding:utf-8

import requests
from lxml import html
import pymongo
import time
import random
from datetime import datetime
import os
import sys
import signal

# from fake_useragent import UserAgent
ua = UserAgent()
print(ua.ie)
print(ua.opera)
print(ua.chrome)
print(ua.google)
print(ua.firefox)
print(ua.safari)
print(ua.random)


# 连接数据库
client = pymongo.MongoClient(host='127.0.0.1', port=27017)
# 指定数据库
db = client.xhc
# 指定集合
collname = db.video_info

# 写入数据库
def insert_data(info):
    result = collname.insert_one(info)
    print(result)


host = 'https://h5.xiaohongchun.com'
def getpage(vid):
    baseurl = '{host}/video?vid={vid}'.format(host=host, vid=vid)
    response = requests.get(baseurl, headers=headers)
    headers = {
        ":method": "GET",
        ":scheme": "https",
        # ":path": "/video?vid=346047",
        ":authority": "h5.xiaohongchun.com",
        # "cookie": "session_id=6677d9388eca4323a5d241a3424bae91",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "upgrade-insecure-requests": "1",
        "User-Agent": ua.random,
        "accept-language": "zh-cn",
        "accept-encoding": "br, gzip, deflate"
    }

    if response.status_code == 200:
        selector = html.fromstring(response.content)

    try:
        # 分析页面获取数据
        # for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
        video = selector.xpath('//div[@id="container"]//video/@src')[0]
        type = selector.xpath('//div[@id="container"]//video/@type')[0]
        poster = selector.xpath('//div[@id="container"]//video/@poster')[0]
        avator = selector.xpath('//div[starts-with(@class, "video_user_info")]/div[starts-with(@class, "left-")]//img/@src')[0]
        username = selector.xpath('//div[starts-with(@class, "video_user_info")]/div[starts-with(@class, "middle-")]//a/text()')[0]
        time = selector.xpath('//div[starts-with(@class, "video_detail-")]/div[starts-with(@class, "middle-")]/span/text()')[0]
        view_count = selector.xpath('//div[starts-with(@class, "video_detail-")]/div[starts-with(@class, "middle-")]/span/text()')[1]
        desc = selector.xpath('//div[starts-with(@class, "vdesc_con-")]/*[starts-with(@class, "desc-")]/text()')[0]
        # 点赞量
        like = selector.xpath('//div[starts-with(@class, "actions-")]/span[starts-with(@class, "like-")]/text()')[0]
        # 收藏量
        # collection = selector.xpath('//div[starts-with(@class, "actions-")]/span[starts-with(@class, "collect-")]/text()')[0]
        collection = selector.xpath('//span[starts-with(@class, "collect-")]/text()')[0]
        print('collection', collection)
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
            'desc': desc,
            'like': like,
            'collection': collection,
            'create_time': datetime.now()
        }
        return info
    except:
        return False


# 获取随机手机 user_agents
def get_user_agent():
    user_agents =  [
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


# 持续调用
def start():
    # 目测视频Id是大于4位的数字
    vid = 2002
    while 1:
        res = getpage(vid)
        if res:
            print('start insert data', res)
            insert_data(res)
        else:
            print('-------res----:', res)
        print('curent vid is: ', vid)
        vid += 1
        time.sleep(random.randint(0,1))


if __name__ == '__main__':
    start()
    # vid = 345879
    # getpage(vid)