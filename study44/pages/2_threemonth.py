import streamlit as st
from crawling.kma import getThreeData

st.set_page_config(
  page_title="기상청 3개월 예보 RSS(XML)",
  page_icon="💗",
  layout="wide",
)

if 'url_index' not in st.session_state:
	st.session_state.url_index = 0

# 기상청 3개월 예보 RSS(XML) URL : 매달 23일에 생성
urls = [
  "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon3rss_108_20251223.xml",
  "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon3rss_108_20260123.xml",
  "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon3rss_108_20260223.xml"
]
options = ("202512","202601","202602")

selected = st.selectbox(
  label="기상청 3개월 예보",
  options=options,
  index=None,
  placeholder="수집 대상을 선택하세요."
)

if selected:
  st.write("선택한 기준 :", selected)
  st.session_state.url_index = options.index(selected)
  if st.button(f"'{options[st.session_state.url_index]}' 수집"):
    url = urls[st.session_state.url_index]
    st.text(url)
    meta_data, df_summary, df_region = getThreeData(url, True)
    tab1, tab2, tab3 = st.tabs(["제목, 예보기간", "전체 주차별 예보 요약", "지역별 상세"])
    with tab1:
       st.json(meta_data)
    with tab2:
      st.dataframe(df_summary)
    with tab3:
      st.dataframe(df_region)
