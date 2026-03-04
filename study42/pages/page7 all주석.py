# ==============================
# 라이브러리 import
# ==============================

import streamlit as st   # 웹앱 프레임워크
import ollama            # 로컬 LLM(Ollama) 연결용 라이브러리


# ==============================
# 페이지 기본 설정
# ==============================

st.set_page_config(
    page_title="6. 로컬 실시간 AI",  # 브라우저 탭 제목
    page_icon="💗",                # 탭 아이콘
    layout="wide",                # 화면을 넓게 사용
)

st.title("[6] 로컬 실시간 AI")  # 페이지 제목 출력


# ==============================
# 대화 기록(session_state) 초기화
# ==============================

# Streamlit은 새로고침하면 변수 초기화됨
# session_state를 사용하면 대화 기록 유지 가능

if "history" not in st.session_state:
    st.session_state["history"] = []  # 대화 내용 저장용 리스트 생성


# ==============================
# 기존 대화 내용 화면에 다시 출력
# ==============================

# 새로고침해도 기존 대화를 다시 그려주기 위함
for msg in st.session_state["history"]:

    # msg["role"] 은 "user" 또는 "assistant"
    with st.chat_message(msg["role"]):

        # msg["content"] 는 실제 대화 텍스트
        st.write(msg["content"])


# ==============================
# 사용자 입력 받기 (채팅 입력창)
# ==============================

# 채팅 입력창 생성
# 사용자가 입력하면 prompt 변수에 저장됨
if prompt := st.chat_input("메시지를 입력하세요"):

    # ------------------------------
    # 1️⃣ 사용자 메시지 화면에 출력
    # ------------------------------
    with st.chat_message("user"):
        st.write(prompt)

    # 대화 기록에 사용자 메시지 저장
    st.session_state["history"].append({
        "role": "user",
        "content": prompt
    })


    # ------------------------------
    # 2️⃣ AI 응답 생성 시작
    # ------------------------------
    with st.chat_message("assistant"):

        # 실시간 출력용 placeholder
        message_placeholder = st.empty()

        # 전체 응답을 누적 저장할 변수
        full_response = ""

        # Ollama 모델 호출 (스트리밍 모드)
        stream = ollama.chat(
            model="gemma3:4b",  # 사용할 모델
            messages=st.session_state["history"],  # 전체 대화 맥락 전달
            stream=True  # 실시간 스트리밍 모드
        )

        # ------------------------------
        # 3️⃣ 스트리밍 응답 처리
        # ------------------------------
        for chunk in stream:

            # chunk 안에 있는 실제 텍스트 추출
            content = chunk["message"]["content"]

            # 기존 응답에 계속 이어붙이기
            full_response += content

            # 실시간으로 화면에 출력
            # ▌ 커서 효과
            message_placeholder.markdown(full_response + "▌")

        # 스트리밍 완료 후 커서 제거
        message_placeholder.markdown(full_response)

        # ------------------------------
        # 4️⃣ AI 응답을 대화 기록에 저장
        # ------------------------------
        st.session_state["history"].append({
            "role": "assistant",
            "content": full_response
        })