from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp
import aiofiles
import os

import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    "Content-Type": "text/html;charset=UTF-8"}

url_template = 'https://nsfwx.pics/page/{}'

folder = '/Users/zcy/PycharmProjects/02_Demo/nsfwx/'


def get_page_asyn(url):
    resp = requests.get(url, headers=headers)
    return resp.text


async def fetch_content(url):
    async with aiohttp.ClientSession(
            headers=headers, connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(url) as response:
            return await response.text()


async def download_one(img_url, index, title):
    cur_folder = folder + title
    if not os.path.exists(cur_folder):
        os.makedirs(cur_folder)

    retry = 5
    times = 0
    while True:
        try:

            async with aiohttp.ClientSession(headers=headers,
                                             connector=aiohttp.TCPConnector(ssl=False)
                                             ) as session:
                async with session.get(img_url) as response:
                    pic = await response.read()
                    img_write_path = cur_folder + str(index) + ".jpg"
                    async with aiofiles.open(img_write_path, mode='wb') as f:
                        await f.write(pic)
                        print('Get res from', img_url, 'Result:', response.status, 'ok!')
                        break
        except(aiohttp.ClientOSError,
               aiohttp.ServerDisconnectedError,
               asyncio.TimeoutError,
               aiohttp.ClientPayloadError
               ):
            if times < retry:
                print("times:{}".format(times))
                times = times + 1
            else:
                raise


async def main():
    html = await fetch_content(url_template.format(1))

    soup = BeautifulSoup(html, 'lxml')
    a_list = soup.find_all('a', {'class': 'featured-img-box'})
    sub_urls = []
    for a in a_list:
        sub_urls.append(a['href'])

    tasks = [fetch_content(sub_url) for sub_url in sub_urls]
    pages = await asyncio.gather(*tasks)

    for page in pages:
        soup_item = BeautifulSoup(page, 'lxml')
        main_div = soup_item.find('div', {'class': 'entry-content'})
        title = soup_item.find('h1', {'class': 'entry-title'}).get_text()
        print(title)
        cur_img_list = []
        img_list = main_div.find_all('img')
        for img in img_list:
            cur_img_list.append(img['src'])
            print(img['src'])

        img_tasks = []
        for index, img_url in enumerate(cur_img_list):
            img_tasks.append(asyncio.create_task(download_one(img_url, index, title)))
        await asyncio.gather(*img_tasks)


start = time.time()
asyncio.run(main())
end = time.time()
print(end - start)
