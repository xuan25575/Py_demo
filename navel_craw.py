import parsel
import requests

url = 'https://www.xbiquge.so/book/47100/'
response = requests.get(url)
# response.encoding = 'utf-8'
# print(response.text)
selector = parsel.Selector(response.text)
navel_name = selector.css("#info h1::text").get()
navel_title_list_href = selector.css("#list dd a::attr(href)").getall()
for link in navel_title_list_href:
    link_url = url + link
    response_1 = requests.get(link_url)
    selector_1 = parsel.Selector(response_1.text)
    title = selector_1.css(".bookname h1::text").get()
    content_list = selector_1.css("#content::text").getall()
    content = '\n'.join(content_list)
    with open(navel_name + '.txt', mode='a', encoding='utf-8') as f:
        f.write(title)
        f.write('\n')
        f.write(content)
        f.write('\n')
    print(title)
