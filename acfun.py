import pprint
import re
import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    "Content-Type": "text/html;charset=UTF-8"}

url = 'https://www.acfun.cn/v/ac36837359'

resp = requests.get(url, headers=headers)

# 提取 m3u8
# 正则表达式一定要有 开始和结束？
data = re.findall(' window.pageInfo = window.videoInfo = (.*?);', resp.text)[0]

json_data = json.loads(data)

# print(json_data)
# 格式化输出 pretty format
# pprint.pprint(json_data)

title = json_data['title']
# 字符串
video_info = json_data['currentVideoInfo']['ksPlayJson']
json_vidio_info = json.loads(video_info)
# pprint.pprint(json_vidio_info)
# m3u8 地址
m3u8_url = json_vidio_info['adaptationSet'][0]['representation'][0]['backupUrl'][0]

# print(title)
# print(m3u8_url)

resp_1 = requests.get(m3u8_url, headers=headers)
# print(resp_1.text)

# '' 替换匹配的到正则
m3u8_data = re.sub('#E.*', '', resp_1.text).split()

for index in m3u8_data:

    ts_url = 'https://tx-safety-video.acfun.cn/mediacloud/acfun/acfun_video/' + index
    # print(ts_url)
    ts_name = index.split(".")[1]
    # resp.content 获取响应体二进制数据
    ts_content = requests.get(ts_url, headers=headers).content
    # print(ts_content)
    # a 追加 b 二进制写入  ab 二进制追加写入
    with open('./' + title + ".mp4", mode='ab') as f:
        f.write(ts_content)

    print(ts_name)
