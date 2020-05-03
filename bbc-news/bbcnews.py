# coding:utf-8

from __future__ import print_function
import requests
import urllib3
from lxml import html
import pymongo
from urllib.parse import urlparse
import re
import time
import random
import json
import os
import configparser
from fake_useragent import UserAgent
# json.dumps(): 对数据进行编码。
# json.loads(): 对数据进行解码。


CONFIG_PATH = os.environ['MONGO_CONFIG_PATH']
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

dburl = 'mongodb://{user}:{password}@{host}:{port}'.format(user = config['MONGODB']['USER'], password = config['MONGODB']['PASSWORD'], host=config['MONGODB']['HOST'],port = config['MONGODB']['PORT'] )
client = pymongo.MongoClient(dburl)

# 指定数据库
db = client.bbcnews
# 文章列表集合
listcoll = db.news_zw
# 文章集合
articlecoll = db.article_zw


def insertList(data):
    for info_item in data:
       _ = listcoll.update_one({'src': info_item['src']}, {"$set": info_item}, True)
    print('--insertArticleList---', _)
    return


def insertArticle(article):
    _ = articlecoll.update_one({'src': article['src']}, {'$set': article}, True)
    # print('--insertArticle---', _)
    return

def getPage(src, referer):
    urlTuple = urlparse(src)
    # 元祖 ParseResult(scheme='https', netloc='www.bbc.com', path='/zhongwen/simp/world-52133520', params='', query='', fragment='')
    headers = {
        "method": "GET",
        "scheme": urlTuple[0],
        "authority": urlTuple[1],
        "path": urlTuple[2],
        "referer": referer,
        "user-agent": UserAgent(verify_ssl=False).random,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'connection': 'close',
        "upgrade-insecure-requests": "1",
        "accept-language": "zh-cn",
        "accept-encoding": "br, gzip, deflate"
    }
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
    s = requests.session()
    # 免费代理
    # https://www.zdaye.com/shanghai_ip.html#Free
    s.proxies = {"https": "117.144.188.207:3128", "http": "101.132.226.199:8080", }
    s.keep_alive = False # 关闭多余连接
    response = s.get(src, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        return None

def parseList(response):
    host = "https://www.bbc.com"
    selector = html.fromstring(response)
    sourceList = selector.xpath('//div[@class="eagle"]/div[contains(@class,"eagle-item")]')

    info_list = []
    for item in sourceList:
        link = item.xpath('.//a[@class="title-link"]/@href')
        imgSrc = item.xpath('.//div[@class="js-delayed-image-load"]/@data-src|//div[contains(@class, "responsive-image")]//img')[0]
        title = item.xpath('.//*[@class="title-link__title-text"]/text()')
        sumery = item.xpath('.//*[@class="eagle-item__summary"]/text()')
        date = item.xpath('.//div[contains(@class, "date--v2")]/@data-datetime')
        dataSecondsStr = item.xpath('.//div[contains(@class, "date--v2")]/@data-seconds')
        dataSeconds = int(dataSecondsStr[0]) if len(dataSecondsStr) else ''

        info = {
            'src': host + link[0] if len(link) else '',
            'img': imgSrc,
            'title':  title[0] if len(title) else '',
            'sumery': sumery[0] if len(sumery) else '',
            'date': date[0] if len(date) else '',
            'data_seconds': dataSeconds
        }
        info_list.append(info)
    return info_list


def getList():
    url = "https://www.bbc.com/zhongwen/simp/world"
    referer = "https://www.bbc.com/zhongwen/simp"
    response = getPage(url, referer)

    if response is None:
        print('--resposne is None--', response)
        return None
    else:
        articleList = parseList(response)
        return articleList

def getTextByList(lists):
    return lists[0] if len(lists) else ''


def getImageAlt(child):
    alt1 = getTextByList(child.xpath('.//figcaption[contains(@class, "media-with-caption__caption")]/text()'))
    alt2 = getTextByList(child.xpath('.//figcaption/span[contains(@class, "media-caption__text")]/text()'))
    alt3 = getTextByList(child.xpath('.//div[contains(@class, "js-delayed-image-load")]/@data-alt'))
    alt4 = getTextByList(child.xpath('.//img/@alt'))

    if alt1:
        alt = alt1.strip()
        return alt
    elif alt2:
        alt = alt2.strip()
        return alt
    elif alt3:
        return alt3
    else:
        return alt4


def parseArticle(response):
    selector = html.fromstring(response)
    mediaPage = selector.xpath('//div[@class="media-asset-page"]')

    if len(mediaPage):
        # 视频页
        articleTitle = selector.xpath('//h1[@class="story-body__h1"]/text()')
        shareContent = selector.xpath('//div[contains(@class, "with-extracted-share-icons")]')[0]
        seconds = shareContent.xpath('.//div[contains(@class, "date--v2")]/@data-seconds')
        dateTime = shareContent.xpath('.//div[contains(@class, "date--v2")]/@data-datetime')
        content = mediaPage[0].xpath('.//div[@class="story-body"]//p/text()')
        article = {
            ## 'src': src,
            'title': articleTitle[0] if len(articleTitle) else '',
            'date_time': dateTime[0] if len(dateTime) else '',
            'seconds': int(seconds[0]) if len(seconds) and seconds[0].isdigit() else '',
            'content': content,
            'type': 'video',
            'images': [],
        }
        print('---article---', article)
        return article
    else:
        # 文章页
        articleTitle = selector.xpath('//h1[@class="story-body__h1"]/text()')
        shareContent = selector.xpath('//div[contains(@class, "with-extracted-share-icons")]')[0]
        seconds = shareContent.xpath('.//div[contains(@class, "date--v2")]/@data-seconds')
        dateTime = shareContent.xpath('.//div[contains(@class, "date--v2")]/@data-datetime')

        storyBody = selector.xpath('//div[@class="story-body"]/div[contains(@class, "story-body__inner")]')
        content = storyBody[0] if len(storyBody) else storyBody
        textList = []
        images = []

        for child in content:
            tag = child.tag
            if tag == 'figure':
                alt = getImageAlt(child)
                src = getTextByList(child.xpath('.//div[contains(@class, "js-delayed-image-load")]/@data-src|.//img/@src'))
                images.append({'src': src, 'alt': alt })
                textList.append('<img>')
            elif tag == 'p':
                text = getTextByList(child.xpath('.//text()'))
                textList.append(text)
            elif tag == 'h2':
                subtitle = getTextByList(child.xpath('.//text()'))
                textList.append('<h2>' + subtitle + '</h2>')
            else:
                pass

        article = {
            # 'src': src,
            'title': articleTitle[0] if len(articleTitle) else '',
            'date_time': dateTime[0] if len(dateTime) else '',
            'seconds': int(seconds[0]) if len(seconds) and seconds[0].isdigit() else '',
            'content': textList,
            'type': "article",
            'images': images,
        }
        # print('---article---', article)
        return article



def getArticle(url):
    print('--url-', url)
    referer = "https://www.bbc.com/zhongwen/simp/world"
    response = getPage(url, referer)

    if response is None:
        print('--resposne is None--', response)
        return None
    else:
        article = parseArticle(response)
        article['src'] = url
        return article


def main():
    articleList = getList()
    if isinstance(articleList, list):
        # 文章列表信息入库
        insertList(articleList)
        # 爬取文章内容
        for item in articleList:
            src = item['src']
            time.sleep(random.uniform(10, 15))
            article = getArticle(src)
            insertArticle(article)

    else:
        print('--获取文章列表出错--')

if __name__ == "__main__":
    main()
    # getArticle("https://www.bbc.com/zhongwen/simp/world-52145754")

    # getArticle("https://www.bbc.com/zhongwen/simp/world-52103102")
    # getArticle("https://www.bbc.com/zhongwen/simp/world-52132483")
    # getArticle("https://www.bbc.com/zhongwen/simp/world-52118220")
