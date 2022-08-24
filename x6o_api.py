import time

import requests
import re
import asyncio
import aiohttp
import aiofiles
import os

# https://www.x6o.com/api/topics/14/articles?page=3&per_page=20&order=-update_time&include=user,topics,is_following


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    "Content-Type": "text/html;charset=UTF-8"}

url_data = 'https://www.x6o.com/api/topics/14/articles?page=3&per_page=20&order=-update_time&include=user,topics,' \
           'is_following '

folder = '/Users/code/crawing/spider_demo/pic3/x6oCom/'


def get_page_sync(url):
    resp = requests.get(url, headers=headers)
    return resp.json()


async def fetch_content(url):
    async with aiohttp.ClientSession(
            headers=headers, connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        resp = await session.get(url)
        return await resp.json()


async def download_one(url, index, title):
    cur_folder = folder + title
    if not os.path.exists(cur_folder):
        os.makedirs(cur_folder)

    retry = 5
    times = 0
    while True:
        try:
            async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=False)
                                             ) as session:
                resp = await session.get(url)
                pic = await resp.read()
                img_path = cur_folder + '/' + str(index) + ".jpg"
                async with aiofiles.open(img_path, mode='wb') as f:
                    await f.write(pic)
                    print('get from url :{}, reps : {} ok !'.format(url, resp.status))
                    break
        except(
                aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError,
                asyncio.TimeoutError,
                aiohttp.ClientPayloadError
        ):
            if retry > times:
                times = times + 1
                print("times:{}".format(times))
            else:
                raise


async def main():
    api_data = await fetch_content(url_data)
    for data in api_data['data']:
        title = data['title']
        print(title)
        content = data['content_markdown']
        pattern = re.compile("(https:.*)")
        img_urls = pattern.findall(content)
        cur_tasks = []
        for index, img_url in enumerate(img_urls):
            cur_tasks.append(asyncio.create_task(download_one(img_url, index, title)))
        await asyncio.gather(*cur_tasks)


start = time.time()
asyncio.run(main())
end = time.time()
print(end - start, 's')
