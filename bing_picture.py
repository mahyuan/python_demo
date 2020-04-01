#!/usr/bin/env python3
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
# client = pymongo.MongoClient(host='127.0.0.1', port=27017)
client = pymongo.MongoClient(host='121.36.170.117', port=27017) # tx
# 指定数据库
db = client.bing
# 指定集合
document = db.wallpaper

maxsize = 1


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


# 查询是否已保存
def search(src):
    result = document.find_one({'src': src})
    return result


# 插入数据库
def insert(info):
    document.insert_one(info)


# 爬取页面
def get_page():
    # us = UserAgent()
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
        # 'User-Agent': us.random,
        'User-Agent': get_user_agent(),
        'Cookie': 'Hm_lvt_667639aad0d4654c92786a241a486361=1548822638; likes=; Hm_lpvt_667639aad0d4654c92786a241a486361=1548822830'
    }

    baseurl = 'https://bing.ioliu.cn'
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(baseurl, headers=headers, verify=False)
    if response.status_code == 200:
        selector = html.fromstring(response.content)
        text = selector.xpath('//div[@class="page"]/span/text()')[0]
        total = int(text.split('/')[1])
        print('total page: ', total)
    else:
        print('response code not 200')
        total = 0

    for pagesize in range(1, total):
        time.sleep(random.uniform(0, 0.005))
        base_url = 'https://bing.ioliu.cn?p={pagesize}'.format(pagesize=str(pagesize))
        response = requests.get(base_url, headers=headers, verify=False)
        print('----pagesize: {pagesize}, --response-: {response} '.format(pagesize=pagesize, response=response))
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

                print('--before search src---', src)
                result = search(src)
                print('result', result)
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
