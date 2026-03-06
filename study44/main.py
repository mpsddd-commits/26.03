import streamlit as st

st.set_page_config(
  page_title="기상청 RSS",
  page_icon="💗",
  layout="wide",
)

st.title("기상청 RSS 프로젝트")

st.subheader("1. 1개월 예보(XML)")
with st.expander("보기"):
  st.page_link(page="./pages/1_onemonth.py", label="[수집 보기]", icon="🔗")
  st.code("""
    ## 기상청 1개월 예보 RSS(XML) URL : 매주 목요일에 생성
    # url = "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon1rss_108_20260219.xml"
    # url = "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon1rss_108_20260226.xml"
    # url = "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon1rss_108_20260305.xml"
  """)

st.subheader("2. 3개월 예보(XML)")
with st.expander("보기"):
  st.page_link(page="./pages/2_threemonth.py", label="[수집 보기]", icon="🔗")
  st.code("""
    ## 기상청 3개월 예보 RSS(XML) URL : 매달 23일에 생성
    # url = "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon3rss_108_20251223.xml"
    # url = "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon3rss_108_20260123.xml"
    # url = "https://www.kma.go.kr/repositary/xml/fct/mon/img/fct_mon3rss_108_20260223.xml"
  """)
