
# from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
import os
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

root_url = 'https://wallhaven.cc/?'
searchUrl = 'https://wallhaven.cc/search?'
#  缩略图 https://th.wallhaven.cc/small/k7/k7p51m.jpg
#  高清大图区别 https://w.wallhaven.cc/full/k7/wallhaven-k7p51m.png
#  k7 -> 【k7】p51m 前两位
#  k7p51m - k7p51m 一样的，路径可以固定
ImgUrl = 'https://w.wallhaven.cc/full/{}/wallhaven-{}'
save_dir = '/Users/code/crawing/spider_demo/pic4/wallhaven/'
headers = {
    "Referer": root_url,
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/63.0.3239.132 Safari/537.36",
    'Accept-Language': 'en-US,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive'
}


# 设置请求saveOneImg的头部，伪装成浏览器

def save_one_img(dir, img_url):
    new_headers = {
        "Referer": img_url,
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/63.0.3239.132 Safari/537.36",
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive'
    }
    # 设置请求的头部，伪装成浏览器，实时换成新的 header 是为了防止403 http code问题，防止反盗链，

    try:
        img = requests.get(img_url, headers=new_headers)  # 请求图片的实际URL
        if str(img).find('200') > 1:
            with open(
                    '{}/{}'.format(dir, img_url.split('/')[-1]), 'wb') as jpg:  # 请求图片并写进去到本地文件
                jpg.write(img.content)
                print(img_url)
                jpg.close()
            return True
        else:
            return False
    except Exception as e:
        print('exception occurs: ' + img_url)
        print(e)
        return False


def process_one_pages(tmp_dir, img_list):
    for img in img_list:
        # code -> k7p51m.jpg
        code = img.get('data-src').split('/')[-1]

        # 拼装高清大图的地址 -> code[:2] ->  k7 前两个字符
        save_one_img(tmp_dir, ImgUrl.format(code[:2], code))
    pass


def one_spider_process(name, tag):
    tmp_dir = '{}/{}'.format(save_dir, name)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    page = 1
    while True:
        params = {
            'q': tag,
            'page': page
        }
        url = searchUrl + urlencode(params)
        print('current page is: %s' % url)
        html = BeautifulSoup(requests.get(url, headers=headers).text, features="html.parser")

        footer = html.find('footer', {'class': 'pagination-notice'})
        if footer is not None:
            break

        img_list = html.find('section', {'class': 'thumb-listing-page'}).find('ul').find_all('img')
        page = page + 1
        process_one_pages(tmp_dir, img_list)


def get_all_tags():
    # 此处应该是从标签页面去获取很多的。为了演示，这里自己手动填写了几个演示一下
    return {'初音未来': 'id:3', '最终幻想VII': 'id:2659', 'Uzumaki Naruto': 'id:1188'}


if __name__ == '__main__':
    tag_list = get_all_tags()

    start = time.time()
    # 给每个标签配备一个线程
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # 创建一个最大容纳数量为20的线程池
        to_do = []
        for name, tag in tag_list.items():
            # 方法 和 参数
            future = executor.submit(one_spider_process, name, tag)
            to_do.append(future)
        # 等待所有线程都完成。
        for future in concurrent.futures.as_completed(future):
            future.result()

    end = time.time()
    print(end - start, 's')
    # test one tag
    # one_spider_process('初音未来', 'id:3')
