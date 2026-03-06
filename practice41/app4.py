from bs4 import BeautifulSoup as bs
from requests import get
from db import save
import json

def getLikes(list, head=None):
  ids = ""
  for i in range(len(list)):
    if i == 0:
      ids += f"{list[i]["id"]}"
    else:
      ids += f",{list[i]["id"]}"
  if ids:
    url = f"https://www.melon.com/commonlike/getSongLike.json?contsIds={ids}"
    res = get(url, headers=head)
    if res.status_code == 200:
      data = json.loads(res.text)
      for row in data["contsLike"]:
        for i in range(len(list)):
          if list[i]["id"] == row["CONTSID"]:
            list[i]["cnt"] = row["SUMMCNT"]
            break
  return list

def getData(data):
  arr = []
  trs = data.select("#frm tbody > tr")
  if trs:
    for i in range(len(trs)):
      id = int(trs[i].select("td")[0].select_one("input[type='checkbox']").get("value"))
      img = cleanData(trs[i].select("td")[2].select_one("img")["src"])
      title = cleanData(trs[i].select("td")[4].select_one("div[class='ellipsis rank01']").text)
      album = cleanData(trs[i].select("td")[5].select_one("div[class='ellipsis rank03']").text)
      arr.append( {"id": id, "img": img, "title": title, "album": album, "cnt": 0} )
  return arr

def cleanData(txt):
  list = ["\n", "\xa0", "\r", "\t", "총건수"]
  for target in list:
    txt = txt.replace(target, "")
  return txt.strip()

def crawlingMelon(gnrCode: str, head=None):
  if head is None:
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
  url = f"https://www.melon.com/genre/song_list.htm?gnrCode={gnrCode}&orderBy=POP"
  res = get(url, headers=head)
  arr = []
  if res.status_code == 200:
    data = bs(res.text)
    arr = getData(data)
    arr = getLikes(arr, head)
    if len(arr) > 0:
      for row in arr:
        sql1 = f"""
            INSERT INTO edu.`info` 
            (`id`, `img`, `title`, `album`, `cnt`)
            VALUE
            ('{row["id"]}', '{row["img"]}', '{row["title"]}', '{row["album"]}', {row["cnt"]});
        """
        save(sql1)
  return arr
  

print( crawlingMelon("GN0100") )