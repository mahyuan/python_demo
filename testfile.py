import os

dirfld = '/Users/mhy/Pictures/bing'
file = "山谷瀑布公园内的蕨菜，美国康涅狄格州_Fiddleheads_ZH-CN14463697077_1920x1080.jpg"
fullp = '{}/{}'.format (dirfld, file)

# 判断目录或文件是否存在
exists = os.path.exists(dirfld)
# 判断文件是否存在
filExists = os.path.isfile(fullp)

print(exists)
print(fullp, filExists)

