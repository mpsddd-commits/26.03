import streamlit as st
import trafilatura as tra
import ollama
import re

# 지금은 BeautifulSoup으로 테이블 구조를 직접 파싱하고 있잖아? 그런데 기사 본문 수집이라면 trafilatura가 훨씬 편해.

st.set_page_config(
	page_title="4. 뉴스기사 요약",
	page_icon="💗",
	layout="wide",
)

st.title("[4] 뉴스기사 요약")

def extract_txt_image(url: str):
	html = tra.fetch_url(url)
	text = tra.extract(html, output_format="markdown", include_comments=False)
	image = tra.extract_metadata(html).image
	return text, image

# 예시 : https://www.koreaherald.com/article/10685727
# 예시 : https://www.koreaherald.com/article/10686698
if url := st.text_input("주소 입력", placeholder="URL을 입력하세요"):
  text, image = extract_txt_image(url)
  message = ""
  st.image(image)
  if re.search('[ㄱ-ㅎㅏ-ㅣ가-힣]', text):
    message = text 
    st.markdown(message)
  else:
    message_placeholder = st.empty()
    prompt = f"다음 기사를 한글로 번역해주세요:\n {text}"
    stream = ollama.chat(
      model="gemma3:4b",
      messages=[{"role": "user", "content": prompt}],
      stream=True
    )
    full_response = ""
    for chunk in stream:
      content = chunk["message"]["content"]
      full_response += content
      message_placeholder.markdown(full_response + "▌")
		# res = ollama.chat(model="gpt-oss:20b", messages=[{"role":"user","content":prompt}])
		# st.markdown(res.message.content)
    