from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time
import os
import re
import hashlib
import shutil

path_img = '/Users/zcy/PycharmProjects/02_Demo/tuiimg'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    "Content-Type": "text/html;charset=UTF-8"}

# 爬取所有
page_template_url = 'https://www.tuiimg.com/meinv/list_{}.html'


async def fetch_content(url):
    async with aiohttp.ClientSession(
            headers=headers, connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(url) as resp:
            return await resp.text()


async def download_one(url):
    max_retries = 5
    attempt = 0
    while True:
        try:
            async with aiohttp.ClientSession(
                    headers=headers, connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.get(url) as resp:
                    # 读取2进制流
                    pic = await resp.read()
                    # image_guid = hashlib.sha1(url.encode('utf-8')).hexdigest()
                    # img_path_name = "{}{}".format('/Users/zcy/PycharmProjects/02_Demo/tuiimg/',
                    #                               "{}{}".format(image_guid, os.path.splitext(url)[-1]))
                    # async with open(img_path_name, 'wb') as f:
                    #     await f.write(pic)
                    await write_pic(url, pic)
            print('Get res from', url, 'Result:', resp.status, 'ok!')
            break
        except (
                aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError,
                asyncio.TimeoutError,
                aiohttp.ClientPayloadError
        ):
            if attempt < max_retries:
                print("times:{}".format(attempt))
                # time.sleep(1)
                attempt += 1
            else:
                raise


async def write_pic(url, pic):
    image_guid = hashlib.sha1(url.encode('utf-8')).hexdigest()
    img_path_name = "{}{}".format('//Users/zcy/PycharmProjects/02_Demo/tuiimg/',
                                  "{}{}".format(image_guid, os.path.splitext(url)[-1]))
    with open(img_path_name, 'wb') as f:
        f.write(pic)


async def main():

    # url => https://www.tuiimg.com/meinv/list_1.html
    # url => https://www.tuiimg.com/meinv/list_2.html
    url = 'https://www.tuiimg.com/meinv/'
    text = await fetch_content(url)
    bs_1 = BeautifulSoup(text, 'lxml')
    a_all = bs_1.find_all('a', {'class': 'pic'})
    detail_urls = []
    for a in a_all:
        detail_urls.append(a['href'])

    print(detail_urls)
    tasks = [fetch_content(detail_url) for detail_url in detail_urls]
    pages = await asyncio.gather(*tasks)
    img_urls = []
    for page in pages:
        bs_2 = BeautifulSoup(page, 'lxml')
        div = bs_2.find("div", {'class': 'content'})
        img_init_link = div.find("img")['src']
        # print(img_init_link)
        # print(img_init_link[0:-5])
        # print(os.path.splitext(img_init_link))
        text = bs_2.find("i", id='allbtn').get_text()
        pattern = re.compile("\((.*?)\)")
        total = pattern.search(text).group(1).split("/")[1]
        for i in range(1, int(total) + 1):
            img_url = img_init_link[0:-5] + str(i) + '.jpg'
            img_urls.append(img_url)

    print(len(img_urls))
    tasks_img = [download_one(img_url) for img_url in img_urls]
    await asyncio.gather(*tasks_img)


start = time.time()
asyncio.run(main())
end = time.time()
print(end - start, 's')  # 300 s
