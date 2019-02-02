#!/bin/bash

echo -e "\033[31m-----------开始执行爬取数据脚本了-----------\033[0m"
python3 /Users/mhy/private/python_demo/bing_picture.py

if [ $? -eq 0 ]; then
	echo -e "\033[35m--------爬取数据成功了，现在下载图片-----------\033[0m"
  	rm -rf /Users/mhy/Pictures/bing/*
	python3 /Users/mhy/private/python_demo/dowload_picture.py
else
	echo  -e "\033[35m-----------爬取数据失败-----------\033[0m"
fi

echo -e "\033[032m-----------下载图片完成了----------------\033[0m"
