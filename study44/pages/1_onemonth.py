import streamlit as st
from crawling.kma import getOneData

st.set_page_config(
  page_title="기상청 1개월 예보 RSS(XML)",
  page_icon="💗",
  layout="wide",
)

if 'url_index' not in st.session_state:
	st.session_state.url_index = 0

# 기상청 1개월 예보 RSS(XML) URL : 매주 목요일에 생성
urls = [
  "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon1rss_108_20260219.xml",
  "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon1rss_108_20260226.xml",
  "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon1rss_108_20260305.xml"
]
options = ("2026-02-19","2026-02-26","2026-03-05")

selected = st.selectbox(
  label="기상청 1개월 예보",
  options=options,
  index=None,
  placeholder="수집 대상을 선택하세요."
)

if selected:
  st.write("선택한 기준 :", selected)
  st.session_state.url_index = options.index(selected)
  if st.button(f"'{options[st.session_state.url_index]}' 수집"):
    url = urls[st.session_state.url_index]
    meta_data, df_summary, df_region = getOneData(url)
    tab1, tab2, tab3 = st.tabs(["제목, 예보기간", "전체 주차별 예보 요약", "지역별 상세"])
    with tab1:
       st.json(meta_data)
    with tab2:
      st.dataframe(df_summary)
    with tab3:
      st.dataframe(df_region)
