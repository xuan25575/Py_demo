from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time
import os
import re
import hashlib
import shutil

path_img = '/Users/zcy/PycharmProjects/02_Demo/tuiimg2/'

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


async def download_one(url, title, pic_name):
    cur_path_img = path_img + title
    # print(cur_path_img)
    if not os.path.exists(cur_path_img):
        os.makedirs(cur_path_img)
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
                    await write_pic(cur_path_img, pic_name, pic)
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

async def write_pic(path, pic_name, pic):
    img_path_name = path + '/' + pic_name
    with open(img_path_name, 'wb') as f:
        f.write(pic)


async def main():
    # url => https://www.tuiimg.com/meinv/list_1.html
    # url => https://www.tuiimg.com/meinv/list_2.html
    url = 'https://www.tuiimg.com/meinv/list_2.html'
    text = await fetch_content(url)
    bs_1 = BeautifulSoup(text, 'lxml')
    a_all = bs_1.find_all('a', {'class': 'pic'})
    detail_urls = []
    for a in a_all:
        detail_urls.append(a['href'])

    # print(detail_urls)
    tasks = [fetch_content(detail_url) for detail_url in detail_urls]
    pages = await asyncio.gather(*tasks)
    # 套图爬取
    for page in pages:
        img_urls = []
        bs_2 = BeautifulSoup(page, 'lxml')
        title = bs_2.find('h1').get_text()
        print(title)
        div = bs_2.find("div", {'class': 'content'})
        img_init_link = div.find("img")['src']
        # print(img_init_link)
        # print(img_init_link[0:-5])
        # print(os.path.splitext(img_init_link))
        text = bs_2.find("i", id='allbtn').get_text()
        pattern = re.compile("\((.*?)\)")
        total = pattern.search(text).group(1).split("/")[1]
        pic_names = []
        for i in range(1, int(total) + 1):
            pic_names.append(str(i) + '.jpg')
            img_url = img_init_link[0:-5] + str(i) + '.jpg'
            img_urls.append(img_url)

        tasks_img = []
        for index, img_url in zip(pic_names, img_urls):
            tasks_img.append(download_one(img_url, title, index))
        await asyncio.gather(*tasks_img)

    print(len(img_urls))


start = time.time()
asyncio.run(main())
end = time.time()
print(end - start, 's')  # 300 s
