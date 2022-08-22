import hashlib
import shutil
import requests
from bs4 import BeautifulSoup
import re

import asyncio
import aiohttp
import time
import os

mm_folder = "/Users/life/pic/x6o/"
url_page_template = "/Users/life/pic/x6o/{}/{}/"

fetch_url = "https://www.x6o.com/articles"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    "Content-Type": "text/html;charset=UTF-8"}


async def fetch_content(url):
    async with aiohttp.ClientSession(
            headers=headers, connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(url) as response:
            return await response.text()


async def download_one(url):
    max_retries = 5
    attempt = 0
    while True:
        try:
            async with aiohttp.ClientSession(
                    headers=headers, connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.get(url) as resp:
                    pic = await resp.read()

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
    img_path_name = "{}{}".format('/Users/life/pic/x6o/',
                                  "{}{}".format(image_guid, os.path.splitext(url)[-1]))
    with open(img_path_name, 'wb') as f:
        f.write(pic)


async def main():
    url = "https://www.x6o.com/articles"
    init_page = await fetch_content(url)
    # print(init_page)
    init_soup = BeautifulSoup(init_page, 'lxml')
    urls_to_fetch = []
    all_articles = init_soup.find_all('a', {'class': 'mc-list-item'})
    for articles in all_articles:
        urls_to_fetch.append('https://www.x6o.com' + str(articles['href']))

    tasks = [fetch_content(url) for url in urls_to_fetch]
    pages = await asyncio.gather(*tasks)

    pic_url = []
    for page in pages:
        soup_item = BeautifulSoup(page, 'lxml')
        img_dev = soup_item.find('div', {'class': 'mdui-typo content'})
        for pic in img_dev.find_all('img'):
            print(pic['src'])
            pic_url.append(pic['src'])

    tasks_new = [asyncio.create_task(download_one(site)) for site in pic_url]
    await asyncio.gather(*tasks_new)


start = time.time()
asyncio.run(main())
end = time.time()
print(end - start)

# def fetch_content(url):
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, 'lxml')
#     a_list = soup.findAll('a', {'class': 'mc-list-item'})
#     for a in a_list:
#         sub_url = 'https://www.x6o.com' + a['href']
#         response_1 = requests.get(sub_url, headers=headers)
#         soup_1 = BeautifulSoup(response_1.text, 'lxml')
#         all_pic = soup_1.findAll('img', {'src': re.compile(".*\.jpg")})
#         for pic in all_pic:
#             print(pic['src'])
#
#         break
