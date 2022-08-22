import aiohttp
import asyncio
import os
import time
from lxml import etree

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    "Content-Type": "text/html;charset=UTF-8"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
proxy_1 = 'http://127.0.0.1:7890'


async def fetch_content(url):
    async with aiohttp.ClientSession(
            headers=headers, connector=aiohttp.TCPConnector(ssl=False, limit=20)
    ) as session:
        async with session.get(url) as response:
            return await response.text()


class Aio_app(object):

    def __init__(self):
        self.mm_folder = '/Users/life/pic/everiaclub/{}/'
        self.url_page_template = "https://everia.club/page/{}"
        self.each_limit = 60
        self.total = 0

    async def async_get(self, img_url, title, index):
        title = title.replace("[", "【").replace("]", "】").replace(
            "/", " ").replace("?", "").replace("*", " ").replace(":", " ").replace("|", " ").strip()
        img_folder = self.mm_folder.format(title)
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
        max_retries = 5
        attempt = 0
        while True:
            try:
                # 开启一个 session
                # async with aiohttp.ClientSession() as session:
                async with aiohttp.ClientSession(
                        headers=headers, connector=aiohttp.TCPConnector(ssl=False)
                ) as session:
                    print('Waiting for', img_url)
                    # await 手工挂起，  header  UA 伪装   参数 params /data  proxy
                    response = await session.get(img_url, headers=headers)
                    # await 手工挂起
                    pic = await response.read()
                if response.status == 404:
                    return '404 not found!'
                img_path_name = "{}{}".format(img_folder,
                                              "{}{}".format(str(index).rjust(3, '0'), os.path.splitext(img_url)[-1]))
                await self.write_pic(img_path_name, pic)
                print('Get res from', img_url, 'Result:', response.status, 'ok!')
                break
            except (
                    aiohttp.ClientOSError,
                    aiohttp.ServerDisconnectedError,
                    asyncio.TimeoutError,
            ):
                if attempt < max_retries:
                    print("times:{}".format(attempt))
                    # time.sleep(1)
                    attempt += 1
                else:
                    raise

    async def write_pic(self, img_path_name, pic):
        if os.path.splitext(img_path_name)[-1] == "":
            img_path_name += ".jpg"
        # os.path.exists 判断绝对路径是否存在
        if not os.path.exists(img_path_name):
            with open(img_path_name, 'wb') as pp:
                pp.write(pic)

    async def make_url(self, mm_url, title):
        text = await fetch_content(mm_url)
        # 列表生成器
        htmldata = etree.HTML(text)
        tasks = []
        img_list = htmldata.xpath('//figure[@class="wp-block-image size-large"]/img')
        i = 1
        print("img_list: {}".format(len(img_list)))
        self.total = self.total + len(img_list)
        for img in img_list:
            img_url = img.xpath('@src')[0]
            tasks.append(asyncio.create_task(self.async_get(img_url, title, i)))
            i = i + 1
        await asyncio.gather(*tasks)

    async def page_read(self, page):
        page_url_real = self.url_page_template.format(page)
        text = await fetch_content(page_url_real)
        htmls = etree.HTML(text)
        items = htmls.xpath('//div[@class="content"]')
        sites = []
        titles = []
        tasks = []
        for item in items:
            title = item.xpath('h2/a/text()')[0]
            titles.append(title)
            href = item.xpath('div/a/@href')
            if len(href) == 0:
                continue
            sub_url = href[0]
            sites.append(sub_url)
            # asyncio.run(self.make_url(sub_url, title))
            # await self.make_url(sub_url, title)
            tasks.append(asyncio.create_task(self.make_url(sub_url, title)))
            # break

        # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        #     to_do = []
        #     for site, title in zip(sites, titles):
        #         future = executor.submit(self.make_url, site, title)
        #         to_do.append(future)
        #
        #     for future in concurrent.futures.as_completed(to_do):
        #         future.result()

        # print("task_size:{}".format(len(tasks)))
        done, pending = await asyncio.wait(tasks, timeout=None)
        print(done)
        print(pending)


if __name__ == '__main__':
    app = Aio_app()
    start_time = time.perf_counter()
    asyncio.run(app.page_read(5))
    end_time = time.perf_counter()
    print("totalPic:{} ".format(app.total))
    print('爬取任务已完成,消耗时间:', end_time - start_time)
