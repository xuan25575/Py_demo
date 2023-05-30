import requests
import aiohttp
import asyncio


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


# your spider code
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
}


def get_proxy_ip() -> str:
    proxy = get_proxy().get("proxy")
    proxy_ip = "http://{}".format(proxy)
    return proxy, proxy_ip


def getHtml(url: str):
    # ....
    retry_count = 5
    proxy = get_proxy().get("proxy")
    # print(proxy)
    while retry_count > 0:
        try:
            html = requests.get(url,
                                headers=headers, proxies={"http": "http://{}".format(proxy)})
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    # 删除代理池中代理
    delete_proxy(proxy)
    return None


# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # 加上这一行,解决使用代理请求 https会报错问题

async def getConent(url: str):
    proxy = get_proxy().get("proxy")
    # print('proxy:' + proxy)
    # print('url:' + url)
    retry_count = 6
    while retry_count > 0:
        try:
            async with aiohttp.ClientSession(headers=headers,
                                             connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(url, timeout=5, proxy='http://{}'.format(proxy)) as response:
                    # content = await response.read()
                    # return content
                    return await response.read()
        except (Exception):
            # print("剩余尝试 {} 次".format(retry_count))
            retry_count -= 1

    delete_proxy(proxy)
    if retry_count == 0:
        # print('开始切换为普通模式')
        retry_count = 3
        while retry_count > 0:
            try:
                async with aiohttp.ClientSession(headers=headers,
                                                connector=aiohttp.TCPConnector(ssl=False)) as session:
                    async with session.get(url) as response:
                        return await response.read()
            except aiohttp.ClientPayloadError:
                await session.close()
                async with aiohttp.ClientSession(headers=headers,
                                                connector=aiohttp.TCPConnector(ssl=False)) as session:
                    async with session.get(url) as response:
                        return await response.read()
            except Exception:
                retry_count -= 1
    return None


# if __name__ == '__main__':
#     # conent = getHtml()
#     content = await getConent('https://i.1ooo.me/ac/nrzj/img/2020/02/20200204335810.jpg')
#     print(content)
# async def main():
    #content = await getConent(
    #   'https://i.1ooo.me/ac/nrzj/img/2020/02/20200204335810.jpg')
    # print(content) 
    # proxy = get_proxy().get('proxy')
    # async with aiohttp.ClientSession() as session:
    #     async with session.get("https://i.1ooo.me/ac/nrzj/img/2020/02/20200204335810.jpg",
    #                         proxy="http://{}".format(proxy)) as resp:
    #         print(resp.status)


# asyncio.run(main())