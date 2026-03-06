from bs4 import BeautifulSoup as bs
from requests import get
import pandas as pd
import streamlit as st
import json
from db import saveMany

st.set_page_config(
  page_title="yes24 수집",
  page_icon="💗",
  layout="wide",
)

if 'books_index' not in st.session_state:
	st.session_state.books_index = 0
    
week_links = [  "1157", "1156", "1155", "1154", "1153", "1152", "1151", "1151", "1150", "1149"	]
options = ["02월 23일 ~ 03월 01일",
  "02월 16일 ~ 02월 22일",
  "02월 09일 ~ 02월 15일",
  "02월 02일 ~ 02월 08일",
  "01월 26일 ~ 02월 01일",
  "01월 19일 ~ 01월 25일",
  "01월 12일 ~ 01월 18일",
  "01월 05일 ~ 01월 11일",
  "12월 29일 ~ 01월 04일"]

category_map = {
    "국내도서": "001",
    "외국도서": "002",
    "eBook": "017&eBookTp=0",
    "CD/LP": "003",
    "DVD/BD": "004",
    "문구/GIFT": "006",
}

category = st.selectbox(
    label="도서 카테고리 선택",
    options=list(category_map.keys()),
    index=None,
    placeholder="카테고리를 선택하세요."
)

category_no = category_map.get(category)
category_db = category_no.split("&")[0] if category_no else None

# 데이터 수집
def getData():
  try:
    week_no = week_links[st.session_state.books_index]
    url = f"https://www.yes24.com/product/category/weekbestseller?categoryNumber={category_no}&pageNumber=1&pageSize=40&type=week&saleYear=2026&weekNo={week_no}&sex=A&viewMode=thumb"
    st.text(f"URL: {url}")
    head = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    res = get(url, headers=head)
    books = [] # { 도서명, 저자, 별점 }
    if res.status_code == 200:
      st.text("yes24 도서 주간별 베스트 수집 시작!")      
      soup = bs(res.text, "html.parser")
      trs = soup.select("#yesBestList .itemUnit")
      for item in trs:

        # 제목
        title_tag = item.select_one(".gd_name")
        title = title_tag.get_text(strip=True) if title_tag else None

        # 저자
        author = None
        author_span = item.select_one("span.authPub.info_auth")
        if author_span:
            author_tag = author_span.select_one("a")
            author = author_tag.get_text(strip=True) if author_tag else None

        # 별점
        star_span = item.select_one("span.rating_grade")
        star = 0.0
        try:
          star_no = star_span.select_one("em.yes_b") if star_span else None
          if star_span:
              star = float(star_no.get_text(strip=True))
        except:
          star = 0.0
        sales_span = item.select_one("div.info_row.info_rating")
        sale_num = 0
        try:
          sale_num_no = sales_span.select_one("span.saleNum") if sales_span else None
          if sale_num_no:
            sale_text = sale_num_no.get_text(strip=True)
            sale_num = int(sale_text.split()[-1].replace(",", ""))
        except:
          sale_num = 0
        
        
        # if category_map.value() == "006":
        #   books.append({ "상품명": title, "명칭": author, "별점": star })
        # elif category_map.value() == "003":
        #   books.append({ "CD/LP": title, "아티스트": author, "별점": star })
        # elif category_map.value() == "004":
        #   books.append({ "DVD/BD": title, "감독 / 제작사": author, "별점": star })
        # else:
        #   books.append({ "도서명": title, "저자": author, "별점": star })
        books.append({
            "title": title,
            "author": author,
            "star": star,
            "sale_num": sale_num 

        })

      sql = """
      INSERT INTO yes24
      (week_no, title, author, star, category, sale_num)
      VALUES (%s,%s,%s,%s,%s,%s)
      ON DUPLICATE KEY UPDATE
              week_no = VALUES(week_no),
              title = VALUES(title),
              author = VALUES(author),
              star = VALUES(star),
              category = VALUES(category),
              sale_num = VALUES(sale_num)
      """
      values = [
          (week_no, book["title"], book["author"], book["star"], category_no, book["sale_num"])
          for book in books
      ]
      saveMany(None, sql, values)

      tab1, tab2, tab3, tab4 = st.tabs(["HTML 데이터", "JSON 데이터", "DataFrame","판매 지수 차트"])
      with tab1:
        st.text("html 출력")
        st.html(trs)
      with tab2:
        st.text("JSON 출력")
        json_string = json.dumps(books, ensure_ascii=False, indent=2)
        st.json(body=json_string, expanded=True, width="stretch")
      with tab3:
        st.text("DataFrame 출력")
        st.dataframe(pd.DataFrame(books))
      with tab4:
        st.text("판매 지수 차트")
        st.header(f"{selected and category} 주별 베스트 판매지수 차트")
        df = pd.DataFrame(books)
        st.bar_chart(df, x="title", y="판매 부수", stack=False)
  except Exception as e:
    return 0
  return 1

selected = st.selectbox(label="주간 날짜", 
	options=options,
	index=None,
	placeholder="수집 날짜를 선택하세요.")

if selected and category:
    st.session_state.books_index = options.index(selected)
    if st.button(f"{category} 주간 도서 랭킹 '{options[st.session_state.books_index]}' 수집"):
        if getData() == 0:
            st.text("수집된 데이터가 없습니다.")
