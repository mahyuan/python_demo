#!/bin/bash

echo -e "\033[31m-----------开始执行爬取数据脚本了-----------\033[0m"

flod_home="/Users/mhy/workspace/python_floder/python_demo"
flod_work="/Users/mhy/private/python_demo/"

read -p '1.家里电脑;  2.公司电脑 [h/w] :' f
case ${f} in
    [h])
        fld=/Users/mhy/workspace/python_floder/python_demo
        ;;
    [w])
        fld=/Users/mhy/private/python_demo
        ;;
    *)
esac

echo "${fld}"
echo '开始爬取新数据........'

python3 "${fld}/bing_picture.py"

if [ $? -eq 0 ]; then
    echo -e "\033[35m--------爬取数据成功了，现在下载图片-----------\033[0m"
    rm -rf '~/Pictures/bing/*'
    python3 ${fld}'/dowload_picture.py'
else
    echo  -e "\033[35m-----------爬取数据失败-----------\033[0m"
fi

echo -e "\033[032m-----------下载图片完成了----------------\033[0m"
