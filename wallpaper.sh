#!/bin/bash

# os x系统调整通知
osascript -e 'display notification "Bing 爬虫开始执行" with title "通知" subtitle ""'

flod_home="/Users/mhy/workspace/python_floder/python_demo"
flod_work="/Users/mhy/private/python_demo/"
log="/Users/mhy/logs/wallpaper.log"

date '+%Y'/'%m'/'%d %H':'%M':'%S'': wallpaper' | tee -a -i ${log}
echo -e "\033[31m-----------开始执行爬取数据脚本了-----------\033[0m"

if [ -d ${flod_home} ]; then
    fld=${flod_home}
elif [ -d ${flod_work} ]; then
    fld=${flod_work}
else
    exit 0
    echo "not exists this floader"
fi

echo '开始爬取新数据........'
python3 "${fld}/bing_picture.py"
if [ $? -eq 0 ]; then
    echo -e "\033[35m--------爬取数据成功了，现在下载图片-----------\033[0m"
    python3 ${fld}'/dowload_picture.py'
else
    echo  -e "\033[35m-----------爬取数据失败-----------\033[0m"
fi

osascript -e 'display notification "Bing 爬虫执行完了" with title "通知" subtitle ""'

echo -e "\033[032m-----------下载图片完成了----------------\033[0m"
