#!/usr/bin/python
# coding:utf-8

import requests
import re
from lxml import html
import pymongo
import random
from datetime import datetime
import urllib3
import time


host = 'https://h5.xiaohongchun.com'

# client = pymongo.MongoClient(host='127.0.0.1', port=27017)
client = pymongo.MongoClient(host='121.36.170.117', port=27017) # huaweiyun
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
    # proxies = {'http': 'http://119.101.125.248', 'https': 'https://119.101.125.226'}
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

