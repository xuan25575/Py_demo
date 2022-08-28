import pprint
import time
import requests
import json
import os
import re
import subprocess
from bs4 import BeautifulSoup
import threading

headers = {
    'user-agent': 'Mozilla/5.0',
    'Referer': 'https://www.bilibili.com/'
}

# url = 'https://www.bilibili.com/bangumi/play/ep471915?from_spmid=666.25.episode.0&from_outer_spmid=333.337.0.0'


url = 'https://www.bilibili.com/bangumi/play/ep471914'


# 单视频爬取,然后调用保存mp3和mp4的函数(这里参数使用了可变参数,因为多集还需要传入集数的标题,单集的只需要视频标题就行了)
def read_video(video_url, *title):
    html = requests.get(video_url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    if len(title) == 0:
        title = soup.find("div", {'class': 'media-right'}).find("a").get_text()

    # 很显然 window.__playinfo__=后面的是一个json格式的数据只要用正则表达式提取出来再转化格式很容易就提取到url。
    re_video_str = re.findall('<script>window.__playinfo__=(.*?)</script>', html)[0]
    jsonVideo = json.loads(re_video_str)  # 转换为json格式的数据
    # pprint.pprint(jsonVideo)
    # 单视频的音频url不变的
    audio_url = jsonVideo['data']['dash']['audio'][0]['baseUrl']
    # 视频清晰度和对应的id
    clarity, id01 = jsonVideo['data']['accept_description'], jsonVideo['data']['accept_quality']
    # 将id个视频清晰度作为字典对象,方便等会的提示
    dict_clarity_id = dict(zip(id01, clarity))
    print('该视频清晰度有：', dict_clarity_id)
    # 得到所有的视频数据列表
    all_video_data = jsonVideo['data']['dash']['video']
    # 设置一个存放最大id值变量
    max_id = 0
    # 直接获取视频的最高清晰度id(b站规律,第一个id就是能爬取到的最大值)
    for i in all_video_data:
        max_id = i['id']
        break
    print(f'视频默认获取的最高视频清晰度：', dict_clarity_id[max_id])
    # 遍历单视频的json格式数据，将max_clarity清晰度的视频提取出来
    for i2 in all_video_data:
        if max_id == i2['id']:
            # 调用保存本地的函数(参数: 音频url,视频url,标题(集数或视频))
            save_mp3_mp4(audio_url, i2['baseUrl'], title)
            break


# 设置命名格式正则的sub方法作用: 特殊字符转换为_
def named(title):
    return re.sub(r'[?\\/:!<>|"\s]', '_', title)


# 存储音频、视频(的title参数在单集和多集中是不一样的)
def save_mp3_mp4(mp3_url, mp4_url, title):
    # 调用重命名格式函数--得到的视频标题，这是单视频存储
    title = named(str(title[0]))
    path_create = fr'/Users/code/crawing/spider_demo/b站/bilibili/动漫/{title}/'
    path_generate = fr'/Users/code/crawing/spider_demo/b站/bilibili/动漫/{title}/{title}'
    if not os.path.exists(fr'{path_create}'):
        os.makedirs(fr'{path_create}')
    thread_list = []
    t1 = threading.Thread(target=fetch_mp3, args=(mp3_url, path_generate, title))
    thread_list.append(t1)
    t2 = threading.Thread(target=fetch_mp4, args=(mp4_url, path_generate, title))
    thread_list.append(t2)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()
    # fetch_mp3(mp3_url, path_generate, title)
    # fetch_mp4(mp4_url, path_generate, title)
    # 调用合并文件函数(将路径传入)
    merge(path_generate)


def fetch_mp4(mp4_url, path_generate, title):
    with open(fr'{path_generate}.mp4', 'ab') as f2:
        time.sleep(3)
        f2.write(requests.get(mp4_url, headers=headers).content)
        print(f'{title} -- 视频爬取成功！')


def fetch_mp3(mp3_url, path_generate, title):
    with open(fr'{path_generate}.mp3', 'ab') as f1:
        time.sleep(3)
        f1.write(requests.get(mp3_url, headers=headers).content)
        print(f'{title} --音频爬取成功！')


# 合并视频(传入的参数是视频路径,不过这个前缀不包括.mp3这些结尾)
def merge(path_generate):
    mp3_address = fr'{path_generate}.mp3'
    mp4_address = fr'{path_generate}.mp4'
    merge_address = fr'{path_generate}--合并.mp4'
    command = f'ffmpeg -i {mp3_address} -i {mp4_address} -c:v copy -c:a aac -strict experimental {merge_address}'
    # print(command)
    # subprocess.run(command, shell=True)
    # r = subprocess.Popen(command, shell=True)
    # print(r.stdout)
    # print(r.stderr)
    # 输出数字为 0，表示正确执行；
    # 输出数字非 0，表示错误执行
    os.system(command)
    print(f'{merge_address}合并成功！')


if __name__ == '__main__':
    read_video(url, "凡人修仙传63集")
