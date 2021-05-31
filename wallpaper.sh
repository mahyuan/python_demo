#!/bin/bash

# 执行必应壁纸爬取和下载的脚本，可以配合crontab

# os x系统调整通知
osascript -e 'display notification "Bing 爬虫开始执行" with title "通知" subtitle ""'

user="$USER"
script_flod="/Users/${user}/private/python_demo/bing"

log="/Users/${user}/logs/wallpaper.log"

date '+%Y'/'%m'/'%d %H':'%M':'%S'': wallpaper' | tee -a -i ${log}
echo -e "\033[31m-----------开始执行爬取数据脚本了-----------\033[0m"

if [ -d ${script_flod} ]; then
    echo "script flod is ${script_flod}"
else
    echo "flod not exists, ${script_flod}"
    exit 0
fi


echo '开始爬取新数据........'
python3 "${script_flod}/bing_picture.py"
if [ $? -eq 0 ]; then
    echo -e "\033[35m--------爬取数据成功了，现在下载图片-----------\033[0m"
    python3 ${script_flod}'/dowload_picture.py'
else
    echo  -e "\033[35m-----------爬取数据失败-----------\033[0m"
fi

osascript -e 'display notification "Bing 爬虫执行完了" with title "通知" subtitle ""'

echo -e "\033[032m-----------下载图片完成了----------------\033[0m"
