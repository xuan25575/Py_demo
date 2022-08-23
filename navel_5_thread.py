import requests
import time
from lxml import etree
from threading import Thread
from queue import Queue


# 问题的根本原因在于：因为爬取和保存的一致性，混乱的爬取顺序使得保存顺序也变得混乱。
# 解决方案：将爬取过程和保存过程分离，多线程爬取数据，但按顺序保存数据。
#
# 具体过程:
#
# 爬取目录页，抽取出所有的章节链接。
# 将所有待爬取的链接扔到一个队列里面去，同时给每个链接一个标记。
# 开5个线程，不断地从队列里面拿链接进行爬取。
# 单个章节爬取之后，让爬取这个链接的线程阻塞。
# 申明一个成员变量，表示保存的章节序号，从-1开始
# 当前线程的链接标记是否刚好比章节序号大于1，是就保存，不是就继续阻塞
# 因为是从队列中取数据，就能够保证这5个章节是还没有被爬取的前5个章节
# 代码整体上并不复杂，用的也是requests+lxml的经典组合，主要是队列数据写入和线程阻塞那里，能够理解整个也就不难了。
# 如果是锻炼技术的话可以多线程爬这玩玩，但如果要写全网爬虫，还是写个单线程吧，尤其是在自己时间足够充裕的情况下，毕竟人家租个服务器也不容易。




class MyThread(Thread):
    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        global index
        while not self.q.empty():
            data = self.q.get()

            # 小说地址
            url = ''.join(data[1])
            print(url)

            response = requests.get(url=url, headers=headers).text
            tree = etree.HTML(response)
            title = tree.xpath('//h1/text()')[0]
            text = tree.xpath('//div[@id="content"]//text()')
            text = '\n'.join(text)
            text = text.replace('\\xa0', '').replace("'", '').replace('笔趣阁 www.xbiquge.so，最快更新天下第九 ！',
                                                                      '').replace('[', '')

            while data[0] > index + 1:
                pass
            if data[0] == index + 1:
                print(f'保存{title}')
                # print(f'保存{title}->{text}')
                f.write('\n' + title + '\n')
                f.write(text)
                index += 1


if __name__ == '__main__':
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    index = -1
    url = 'https://www.xbiquge.so/book/37985/'
    resp = requests.get(url, headers=headers).text
    tree = etree.HTML(resp)
    zj_list = tree.xpath('//div[@id="list"]/dl/dd')[12:]
    print(len(zj_list))
    page_urls = []
    for i in zj_list:
        if len(i) == 0:
            continue
        title = i.xpath('./a/text()')[0]  # 章节名
        page_url = 'https://www.xbiquge.so/book/37985/' + i.xpath('./a/@href')[0]
        page_urls.append(page_url)

    start = time.time()
    with open('./天下第九.txt', 'w', encoding='utf-8') as f:
        q = Queue()
        # enumerate组成 带序号的列表
        for i, href in enumerate(page_urls):
            q.put((i, href))

        ts = []

        for i in range(5):
            t = MyThread(q)
            t.start()
            ts.append(t)
        # 等待当前线程章节爬取完毕
        for t in ts:
            t.join()

    end = time.time()
    print(end - start, 's')
