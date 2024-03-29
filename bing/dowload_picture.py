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
        # 'User-Agent': UserAgent(verify_ssl=False).random,
        'User-Agent': get_user_agent(),
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
        dirname = "/Users/mahy/Pictures/bing"
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
