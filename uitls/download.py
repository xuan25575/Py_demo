from typing import List
import os
import asyncio
from urllib.parse import urlparse
import aiofiles
import aiohttp
import time
import proxy
# use 
# sys.path.append('.\\utils\\')
# from download import DownLoad 
# import proxy
#
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}


class DownLoad():

    def __init__(self, image_arr: List, title: str):
        self.image_arr = image_arr
        self.title = title

    async def waitAllTask(self):
        tasks = []
        print("arr len : {0}".format(len(self.image_arr)))
        for i, img_url in enumerate(self.image_arr):
            # tasks.append(asyncio.create_task(
            #     self.download_one(img_url)))
            tasks.append(asyncio.create_task(self.download_one_proxy(img_url)))
        await asyncio.gather(*tasks)

    async def download_one(self, img_url):
        cur_folder = os.getcwd() + '\\images02\\' + self.title
        if not os.path.exists(cur_folder):
            os.makedirs(cur_folder)
        retry = 5
        times = 0
        while True:

            try:
                async with aiohttp.ClientSession(headers=headers,
                                                 connector=aiohttp.TCPConnector(ssl=False)) as session:
                    async with session.get(img_url) as response:
                        pic = await response.read()
                        path = urlparse(img_url).path
                        image_name = os.path.basename(path)
                        if image_name.endswith(".jpg") or image_name.endswith(".jpeg"):
                            file_path = os.path.join(cur_folder, image_name)
                            # print(img_write_path)
                            async with aiofiles.open(file_path, mode='wb') as f:
                                await f.write(pic)
                                print('Get res from', img_url,
                                      'Result:', response.status, 'ok!')
                                break
            except (Exception):
                if times < retry:
                    print("image:{0} get times:{1}".format(img_url, times))
                    times = times + 1
                else:
                    raise

    async def download_one_proxy(self, url):
        cur_folder = os.getcwd() + '\\images02\\' + self.title
        if not os.path.exists(cur_folder):
            os.makedirs(cur_folder)
        content = await proxy.getConent(url)
        # print(resp)
        if content:
            path = urlparse(url).path
            image_name = os.path.basename(path)
            if image_name.endswith(".jpg") or image_name.endswith(".jpeg"):
                # pic = content
                file_path = os.path.join(cur_folder, image_name)
                # print(img_write_path)
                async with aiofiles.open(file_path, mode='wb') as f:
                    await f.write(content)
                    print('Get res from', url, 'ok!')

    def run(self):
        start = time.time()
        asyncio.run(self.waitAllTask())
        end = time.time()
        print('spent ' + str(end - start) + 'ms')
