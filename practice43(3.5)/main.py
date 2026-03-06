import streamlit as st

st.set_page_config(
  page_title="수집",
  page_icon="💗",
  layout="wide",
)

st.title("streamlit 프로젝트")

st.subheader("1. Yes24 베스트셀러 수집")
with st.expander("보기"):
  st.page_link(page="./pages/1_yes24.py", label="[수집 보기]", icon="🔗")
  st.code("""
    def getData():
      try:
        url = ""
        st.text(f"URL: {url}")
        res = get(url)
        if res.status_code == 200:
          st.text("yes24 국내도서 주별 베스트 수집 시작!")
          books = [] # { 도서명, 저자, 별점 }
          tab1, tab2, tab3 = st.tabs(["HTML 데이터", "JSON 데이터", "DataFrame"])
          with tab1:
            st.text("html 출력")
          with tab2:
            st.text("JSON 출력")
          with tab3:
            st.text("DataFrame 출력")
      except Exception as e:
        return 0
      return 1
  """)

st.subheader("2. 인터파크 티켓 수집")
with st.expander("보기"):
  st.page_link(page="./pages/2_interpark.py", label="[수집 보기]", icon="🔗")
  st.code("""
    def getData():
      try:
        url = ""
        st.text(f"URL: {url}")
        res = get(url)
        if res.status_code == 200:
          st.text("인터파크 티켓 수집 시작!")
          tickets = [] # { 장르, 티켓이름, 장소, 시작날짜, 종료날짜, 예매율 }
          tab1, tab2, tab3 = st.tabs(["HTML 데이터", "JSON 데이터", "DataFrame"])
          with tab1:
            st.text("html 출력")
          with tab2:
            st.text("JSON 출력")
          with tab3:
            st.text("DataFrame 출력")
      except Exception as e:
        return 0
      return 1
  """)
