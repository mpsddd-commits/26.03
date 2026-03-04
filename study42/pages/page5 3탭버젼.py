import streamlit as st
import trafilatura as tra
import ollama
import re
import json
import pandas as pd

st.set_page_config(
    page_title="4. 뉴스기사 요약",
    page_icon="💗",
    layout="wide",
)

st.title("[4] 뉴스기사 요약")


# -----------------------------
# 본문 + 이미지 + 메타데이터 추출 함수
# -----------------------------
def extract_txt_image(url: str):
    html = tra.fetch_url(url)  # 원본 HTML 다운로드
    text = tra.extract(
        html,
        output_format="markdown",
        include_comments=False
    )  # 본문 텍스트 추출

    metadata = tra.extract_metadata(html)

    image = metadata.image if metadata else None
    title = metadata.title if metadata else None
    date = metadata.date if metadata else None
    author = metadata.author if metadata else None

    return html, text, image, title, date, author


# -----------------------------
# URL 입력
# -----------------------------
if url := st.text_input("주소 입력", placeholder="URL을 입력하세요"):

    html, text, image, title, date, author = extract_txt_image(url)

    if not text:
        st.error("본문을 추출하지 못했습니다.")
        st.stop()

    # -----------------------------
    # 한글 여부 체크
    # -----------------------------
    if not re.search('[ㄱ-ㅎㅏ-ㅣ가-힣]', text):
        prompt = f"다음 기사를 한글로 번역해주세요:\n {text}"
        stream = ollama.chat(
            model="gemma3:4b",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        translated_text = ""
        for chunk in stream:
            translated_text += chunk["message"]["content"]

        text = translated_text  # 번역 결과로 교체

    # -----------------------------
    # JSON 구조 생성
    # -----------------------------
    article_data = {
        "url": url,
        "title": title,
        "author": author,
        "date": date,
        "image": image,
        "content": text
    }

    # -----------------------------
    # DataFrame 생성
    # -----------------------------
    df = pd.DataFrame([article_data])

    # -----------------------------
    # 탭 생성
    # -----------------------------
    tab1, tab2, tab3 = st.tabs(
        ["HTML 데이터", "JSON 데이터", "DataFrame"]
    )

    # 1️⃣ HTML 원본
    with tab1:
        st.subheader("원본 HTML")
        st.code(html, language="html")

    # 2️⃣ JSON 데이터
    with tab2:
        json_string = json.dumps(
            article_data,
            ensure_ascii=False,
            indent=2
        )

        st.download_button(
            label="JSON 다운로드",
            data=json_string,
            file_name="article.json",
            mime="application/json"
        )

        st.json(article_data)

    # 3️⃣ DataFrame
    with tab3:
        st.dataframe(df, use_container_width=True)