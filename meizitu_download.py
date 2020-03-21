#!/usr/bin/python
# coding:utf-8

import requests
from lxml import html
import os
import time
import sys
import signal


def quit(signum, frame):
    sys.exit()


# 获取主页列表
def getPage(pageNum):
    baseUrl = 'http://www.mzitu.com/page/{}'.format(pageNum)
    selector = html.fromstring(requests.get(baseUrl).content)
    urls = []
    for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
        urls.append(i)
    return urls


# 根据反爬虫的修改，增加下载图片的headers就好了
def header(referer):
    headers = {
        'Host': 'i.meizitu.net',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/59.0.3071.115 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': '{}'.format(referer),
    }
    return headers


# 图片链接列表， 标题
# url是详情页链接
def getPiclink(url):
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    sel = html.fromstring(requests.get(url).content)
    print ('sel', sel)
    # 图片总数
    total = sel.xpath('//div[@class="pagenavi"]/a[last()-1]/span/text()')[0]
    # 标题
    title = sel.xpath('//h2[@class="main-title"]/text()')[0]
    # 接下来的链接放到这个列表
    jpgList = []
    for i in range(int(total)):
        # 每一页
        link = '{}/{}'.format(url, i+1)
        s = html.fromstring(requests.get(link).content)
        # 图片地址在src标签中
        jpg = s.xpath('//div[@class="main-image"]/p/a/img/@src')[0]
        # 图片链接放进列表
        jpgList.append(jpg)
    return title, jpgList


# 下载图片
def downloadPic(title, piclist):
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    k = 1
    # 图片数量
    count = len(piclist)
    # 设置其他地址保存
    abspath = "/Users/mhy/Pictures/meizitu"
    dirName = os.path.join(abspath, '{0}【{1}】'.format(title, count))
    # 新建文件夹
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    else:
        print('dir exists')
    for jpgLink in piclist:
        filename = '%s/%s.jpg' % (dirName, k)
        print(u'开始下载图片:%s 第%s张' % (dirName, k))
        # open的第一个参数指定路径和文件名，第二个参数指定权限相关
        try:
            with open(filename, "wb+") as jpg:
                jpg.write(requests.get(jpgLink, headers=header(jpgLink)).content)
                time.sleep(0.5)
            k += 1
        except KeyboardInterrupt:
            print('下载失败了')
            continue
    print('{} 下载完了'.format(dirName))


if __name__ == '__main__':
    pageNum = input(u'请输入页码：')
    for link in getPage(pageNum):
        try:
            lin = getPiclink(link)
            downloadPic(lin[0], lin[1])
        except KeyboardInterrupt:
            pass
    print('结束了！！！')


    # try:
    #     while 1:
    #         pass
    # except KeyboardInterrupt:
    #     pass
