import streamlit as st # 프로토 타입으로 사용하거나 미니프로젝트 만들고 싶을 때 사용하는데 서비스용으로는 사용하지않고 뷰어용으로 쓴다. 왜냐하면 회원가입이나 로그인이 안 되기 때문이다. 
import time
from bs4 import BeautifulSoup as bs
from requests import get
import json
import pandas as pd
from db import save, saveMany

def getLikes(list, head=None):
  ids = ""
  ids = ",".join(str(item["id"]) for item in list)
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
  txt = txt.replace("'", '"')
  return txt.strip()

st.set_page_config(
    page_title="수집 프로젝트",
    page_icon="💗",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

if 'link_index' not in st.session_state:
	st.session_state.link_index = 0
# 전역함수 설정이라 생각하고 없으면 서로 함수끼리 교신할 수 없다.

st.markdown("<h1 style='text-align: center;'>수집 목록</h1>", unsafe_allow_html=True) # 커스텀 같은 느낌

links = [
  "GN0100",
  "GN0200",
  "GN0300",
  "GN0400",
  "GN0500",
  "GN0600",
  "GN0700",
  "GN0800"  
] # value를 위해 쓴다
options = ("발라드","댄스","랩/힙합","R&B/Soul","인디음악","록/메탈","트로트","포크/블루스") # html 셀렉트 박스를 쓰기 위해 옵션스를 쓴다. html 기초 지식이 있어야한다 w3스쿨즈에 나와있음(html select tag 검색)

def main():
  try:
    st.text("데이터 수집을 시작 합니다.")
    # time.sleep(2) # 2초 뒤에 시작
    # url = links[st.session_state.link_index]
    code = links[st.session_state.link_index]
    url = f"https://www.melon.com/genre/song_list.htm?gnrCode={code}&orderBy=POP"
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
    st.text(url)
    res =get(url, headers=head)
    arr = []
    if res.status_code == 200:
      #st.html(res.text.replace("\n", '').strip())
      data = bs(res.text)
      arr = getData(data)
      arr = getLikes(arr, head)
      if len(arr) > 0:
        for row in arr:
          sql1 = f"""
              INSERT INTO edu.`melon` 
              (`code`, `id`, `img`, `title`, `album`, `cnt`)
              VALUE
              ('{code}', '{row["id"]}', '{row["img"]}', '{row["title"]}', '{row["album"]}', {row["cnt"]});
          """
          #save(sql1)
        sql1 = "TRUNCATE TABLE edu.`melon`"
        sql2 = f"""
            INSERT INTO edu.`melon` 
            (`code`, `id`, `img`, `title`, `album`, `cnt`)
            VALUE
            (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              id=VALUES(id),
              img=VALUES(img),
              title=VALUES(title),
              album=VALUES(album),
              cnt=VALUES(cnt)
        """
        values = [(code, row["id"], row["img"], row["title"], row["album"], row["cnt"]) for row in arr]
        saveMany(None, sql2, values)
        df = pd.DataFrame(arr)
        st.dataframe(df.head(5)) #.head(5) => top5
    st.text("데이터 수집이 완료 되었습니다.")
  except Exception as e:
    return 0
  return arr

selected = st.selectbox(
  label="음원 장르를 선택하세요",
  options=options,
  index=None,
  placeholder="수집 대상을 선택하세요."
) # index=None => placeholder 보이기 위해 선택아무것도 안 한 상태라는 뜻

if selected:
  st.write("선택한 장르 :", selected)
  st.session_state.link_index = options.index(selected)
  if st.button(f"'{options[st.session_state.link_index]}' 수집"): # 버튼은 true,false 두개밖에 없기때문에 if문 사용한다.
    if main() == 0:
      st.text("수집된 데이터가 없습니다.")