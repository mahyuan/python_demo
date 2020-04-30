#!/usr/bin/env python3
# coding:utf-8

# import requests
# from lxml import html
# import os
import time


def get_date():
    t = time.localtime(time.time())
    # print(t)
    date_str = "{y}-{m}-{d}".format(y=t.tm_year, m=t.tm_mon, d=t.tm_mday)
    return date_str


print(get_date())

