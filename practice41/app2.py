from bs4 import BeautifulSoup
import requests

url = 'https://news.naver.com/'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

print(soup.select("div.main_brick div.grid1_wrap brick-house _brick_gid_wrapper div.brick-vowel._brick_column"))


# lis = soup.find_all("li")
# # print(li)

# for li in lis:
#     print( li.find("a").text)

# parents = soup.find("div", class_="grid1_wrap brick-house _brick_gid_wrapper")
# # parents.find_all("div", class_="brick-vowel _brick_column")
# # print(parents)
# parentdiv = parents.find("div", class_="brick-vowel _brick_column", recursive=False)
# print(parentdiv)
# div = parentdiv.find_all("div", class_=" main_brick_item")
# print(div)

# soup = BeautifulSoup(response.text, 'lxml')

# main_brick = soup.find('div', class_='main_brick')

# divs = main_brick.find_all("div", class_="brick-vowel _brick_column")

# i = 0
# for div in divs:
#     if i == 1:
#         print(div)
#     i = i + 1

