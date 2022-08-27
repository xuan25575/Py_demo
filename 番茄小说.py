import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    "Content-Type": "text/html;charset=UTF-8"}

url = 'https://fanqienovel.com/page/6982529841564224526?enter_from=search'
base_url = 'https://fanqienovel.com'
resp = requests.get(url, headers=headers)

soup = BeautifulSoup(resp.text, 'lxml')

div = soup.find("div", {'class': 'page-directory-content'})
div_all = div.find_all("div", {'class': 'chapter-item'})

for chapter_div in div_all:
    href = chapter_div.find("a")['href']
    chapter_url = base_url + href
    resp_1 = requests.get(chapter_url, headers=headers)
    soup_1 = BeautifulSoup(resp_1.text, 'lxml')
    title = soup_1.find('h1', {'class': 'muye-reader-title'}).get_text()
    content = soup_1.find('div', {'class': 'muye-reader-content noselect'}).get_text()
    with open(title + '.txt', mode='w', encoding='utf-8') as f:
        f.write('\n')
        f.write(content)
        f.write('\n')
    break
