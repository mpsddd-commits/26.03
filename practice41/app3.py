from bs4 import BeautifulSoup as bs
from requests import get
import json


url= "https://www.melon.com/genre/song_list.htm"
url2 = "https://www.melon.com/commonlike/getSongLike.json?contsIds=601405898%2C601408401%2C601412950%2C601412107%2C601430732%2C601416574%2C601416570%2C601416535%2C601416271%2C601416261%2C601416212%2C601415215%2C601414111%2C601413850%2C601413800%2C601413798%2C601413742%2C601413738%2C601413550%2C601413408%2C601413390%2C601413333%2C601413080%2C601412960%2C601405270%2C601407441%2C601413060%2C601393896%2C601407916%2C601412828%2C601405642%2C601407906%2C601413104%2C601413051%2C601416316%2C601416284%2C601416282%2C601416281%2C601415505%2C601415360%2C601415299%2C601414109%2C601414105%2C601413819%2C601413249%2C601413233%2C601413216%2C601407817%2C601407812%2C601405239"
# f12에서 getsong뭐시기 있는 주소 가져오면된다.

head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'} # 비동기통신하는 화면에서 받을때 씀. fetch/hxr 안에 headers 안에 리퀘스트 헤더 안에 User-Agent에 있음

res = get(url, headers= head)
res2 = get(url2, headers= head)

ids=[]
imgs = []
titles = []
albums = []
likes = []
cnts = []

if res2.status_code == 200:
    jData= json.loads(res2.text)
    for row in jData["contsLike"]:
        cnts.append({"CONTSID": row["CONTSID"], "SUMMCNT": row["SUMMCNT"]})


if res.status_code == 200:
    data = bs(res.text)
    title = data.title.text
    trs = data.select("#frm tbody > tr") # select문을 사용해서 부모에서 자식 꺼내오세요 (부모 > 자식)
    
    for i in range(len(trs)):
        imgs.append(trs[i].select("td")[2].select_one("img")["src"]) # 멜론 이미지 가져오기
        titles.append(trs[i].select("td")[4].select_one("div[class='ellipsis rank01']").text.replace("\n","").replace("\xa0", " ").strip()) # 멜론 곡명 가져오기 뒤에 줄 넘기기 띄어쓰기 지운 버젼
        albums.append(trs[i].select("td")[5].select_one("div[class='ellipsis rank03']").text.replace("\n","").replace("\xa0", " ").strip()) # 멜론 앨범명 가져오기 뒤에 줄 넘기기 띄어쓰기 지운 버젼
        # likes.append(trs[i].select("td")[6].select_one("span[class='cnt']").text) # 멜론 좋아요 수  가져오기 뒤에 줄 넘기기 띄어쓰기 지운 버젼
        ids.append(int(trs[i].select("td")[0].select_one("input[type='checkbox']").get("value")))

    for id in ids:
        for row in cnts:
            if id ==row["CONTSID"]:
                likes.append(row["SUMMCNT"])
            


# print(imgs)
# print(titles)
# print(albums)
# print(likes)