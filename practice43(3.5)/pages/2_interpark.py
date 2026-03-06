from bs4 import BeautifulSoup as bs
from requests import get
import pandas as pd
import streamlit as st
import json
from db import saveMany

st.set_page_config(
  page_title="interpark 수집",
  page_icon="💗",
  layout="wide",
)

if 'itp_index' not in st.session_state:
	st.session_state.itp_index = 0

genres = [ "MUSICAL", "CONCERT", "CLASSIC", "KIDS", "PLAY", "EXHIBITION" ]
options = [ "뮤지컬", "콘서트", "클래식", "아동", "연극", "전시" ]

# 인터파크 장르별 URL
genre = genres[st.session_state.itp_index]
urls = f"https://tickets.interpark.com/contents/ranking?genre={genre}"
# keys = f'@"/ranking","?period=D&page=1&pageSize=50&rankingTypes={genres[st.session_state.itp_index]}",'



# 데이터 수집
def getData():
  try:
    url = urls
    st.text(f"URL: {url}")
    head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
    res = get(url, headers=head)
    if res.status_code == 200:
      st.text("인터파크 티켓 수집 시작!")
      tickets = [] # { 장르, 티켓이름, 장소, 시작날짜, 종료날짜, 예매율 }
      soup = bs(res.text, "html.parser")
      items = soup.select("div.responsive-ranking-list_rankingItem__PuQPJ")
      genre = genres[st.session_state.itp_index]
      for item in items:
        tName = item.select_one("li.responsive-ranking-list_goodsName__aHHGY").get_text(strip=True)
        pName = item.select_one("li.responsive-ranking-list_placeName__9HN2O").get_text(strip=True)
        tDate = item.select_one("div.responsive-ranking-list_dateWrap__jBu5n").get_text(strip=True)
        tPercent = item.select_one("li.responsive-ranking-list_bookingPercent__7ppKT").get_text(strip=True)
        tickets.append({ "genre": genre, "tName": tName, "pName": pName, "tDate": tDate, "tPercent": tPercent })

    sql = """
    INSERT INTO yes24
    (genre, tName, pName, tDate, tPercent)
    VALUES (%s,%s,%s,%s,%s)
    """
    values = [
        (item["genre"], item["tName"], item["pName"], item["tDate"], item["tPercent"])
        for item in items
    ]
    saveMany(None, sql, values)


    tab1, tab2, tab3, tab4 = st.tabs(["HTML 데이터", "json 데이터", "DataFrame", "API 데이터"])
    with tab1:
      st.text("HTML 출력")
      # st.html(items)
      st.text(items)
    with tab2:
      st.text("JSON 출력")
      # st.json(arr)
      json_string = json.dumps(tickets, ensure_ascii=False, indent=2)
      st.json(body=json_string, expanded=True, width="stretch")
    with tab3:
      st.text("DataFrame 출력")
      st.dataframe(pd.DataFrame(tickets))
    with tab4:
      st.text("API 출력")
      script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
      json_data = json.loads(script_tag.string)
      st.json(json_data, expanded=False)
      st.html("<hr/>")
      st.text(f"{genre} 목록 출력")
      # st.json(json_data.get('props', {}).get('pageProps', {}).get('fallback', {}).get(keys, []), expanded=False)
      fallback = json_data.get("props", {}).get("pageProps", {}).get("fallback", {})
      rank_data = []
      for k, v in fallback.items():
        if "/ranking" in k and genres[st.session_state.itp_index] in k:
          rank_data = v
          break
          
      st.json(rank_data, expanded=False)

  except Exception as e:
    return 0
  return 1

# if st.button(f"수집하기"):
#   getData()

selected = st.selectbox(label="인터파크 장르별 랭킹", 
	options=options,
	index=None,
	placeholder="수집 주별 기준을 선택하세요.")

if selected:
	st.session_state.itp_index = options.index(selected)
	if st.button(f"장르 '{options[st.session_state.itp_index]}' 수집하기"):
		if getData() == 0:
			st.text("수집된 데이터가 없습니다.")