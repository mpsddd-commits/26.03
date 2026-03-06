from bs4 import BeautifulSoup
import requests

url = 'https://www.yes24.com/product/category/weekbestseller'
response = requests.get(url)

# print(response)

soup = BeautifulSoup(response.text, 'lxml')

# print(soup)

# 모든 뉴스 제목 가져오기
titles = soup.select("span.saleNum")

# print(titles)

for t in titles:
    print(t.get_text(strip=True))