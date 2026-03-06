# ==============================
# 라이브러리 import
# ==============================

import streamlit as st        # Streamlit 웹 애플리케이션 프레임워크
import time                   # 시간 제어용 모듈 (현재는 사용 안함)
from requests import get      # HTTP GET 요청 함수
from bs4 import BeautifulSoup as bs  # HTML 파싱용 라이브러리
import json                   # JSON 데이터 변환용
import pandas as pd           # 데이터프레임 생성을 위한 pandas


# ==============================
# 페이지 기본 설정
# ==============================

st.set_page_config(
    page_title="3. 위키백과 수집",  # 브라우저 탭 제목
    page_icon="💗",                # 브라우저 탭 아이콘
    layout="wide",                # 전체 화면 넓게 사용
)


# ==============================
# 세션 상태 초기화
# ==============================

# Streamlit은 새로고침하면 변수 값이 초기화됨
# session_state를 사용하면 상태를 유지할 수 있음
if 'episode_index' not in st.session_state:
    st.session_state.episode_index = 0


# ==============================
# 수집 대상 URL 목록
# ==============================

episode_links = [
    "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_season_1",
    "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_season_2",
    "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_season_3",
    "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_season_4",
]

# 사용자 선택 옵션
options = ["Season1", "Season2", "Season3", "Season4"]


# ==============================
# 데이터 수집 함수
# ==============================

def main():
    try:
        # 수집 시작 메시지 출력
        st.text("데이터 수집을 시작 합니다.")

        # 현재 선택된 시즌의 URL 가져오기
        url = episode_links[st.session_state.episode_index]

        # 위키백과에서 봇 차단 방지를 위한 헤더 설정
        head = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # HTTP GET 요청 보내기
        res = get(url, headers=head)

        # 요청이 정상적으로 성공했는지 확인
        if res.status_code == 200:

            # 에피소드 정보를 저장할 리스트 생성
            episodes = []

            # HTML을 BeautifulSoup 객체로 변환
            soup = bs(res.text)

            # 에피소드 테이블 선택 (CSS 선택자 사용)
            table = soup.select_one(
                "table.wikitable.plainrowheaders.wikiepisodetable"
            )

            # 각 에피소드 행 선택
            rows = table.select("tr.vevent.module-episode-list-row")

            # 에피소드 반복문
            # enumerate(..., start=1) → 에피소드 번호를 1부터 시작
            for i, row in enumerate(rows, start=1):

                synopsis = None  # 줄거리 기본값

                # 에피소드 행 바로 다음 줄에 줄거리 행이 있음
                synopsis_row = row.find_next_sibling(
                    "tr", class_="expand-child"
                )

                # 줄거리 행이 존재하면
                if synopsis_row:
                    synopsis_cell = synopsis_row.select_one(
                        "td.description div.shortSummaryText"
                    )

                    # 줄거리 텍스트 추출
                    synopsis = (
                        synopsis_cell.get_text(strip=True)
                        if synopsis_cell else None
                    )

                # 딕셔너리 형태로 데이터 저장
                episodes.append({
                    "season": options[st.session_state.episode_index],
                    "episode_in_season": i,
                    "synopsis": synopsis
                })

            # ==============================
            # 탭 생성 (3가지 출력 방식)
            # ==============================

            tab1, tab2, tab3 = st.tabs(
                ["HTML 데이터", "JSON 데이터", "DataFrame"]
            )

            # ------------------------------
            # 1️⃣ HTML 원본 테이블 출력
            # ------------------------------
            with tab1:
                st.html(table)

            # ------------------------------
            # 2️⃣ JSON 데이터 출력 및 다운로드
            # ------------------------------
            with tab2:
                # JSON 문자열로 변환
                json_string = json.dumps(
                    episodes,
                    ensure_ascii=False,  # 한글 깨짐 방지
                    indent=2             # 들여쓰기 적용
                )

                # JSON 다운로드 버튼 생성
                st.download_button(
                    label="JSON 다운로드",
                    data=json_string,
                    file_name=f"귀멸의칼날_{options[st.session_state.episode_index]}.json",
                    mime="application/json"
                )

                # JSON을 화면에 보기 좋게 출력
                st.json(
                    body=json_string,
                    expanded=True,
                    width="stretch"
                )

            # ------------------------------
            # 3️⃣ DataFrame 형태로 출력
            # ------------------------------
            with tab3:
                st.dataframe(
                    # season 컬럼은 제거 후 표시
                    pd.DataFrame(episodes).drop(columns=['season']),
                    use_container_width=True
                )

        # 수집 완료 메시지 출력
        st.text("데이터 수집이 완료 되었습니다.")

    # 예외 발생 시 0 반환
    except Exception as e:
        return 0

    # 정상 실행 시 1 반환
    return 1


# ==============================
# UI 구성
# ==============================

# 페이지 제목
st.title("[3] 위키백과 수집")

# 시즌 선택 박스
selected = st.selectbox(
    label="귀멸의 칼날",
    options=options,
    index=None,
    placeholder="수집 대상을 선택하세요."
)

# 시즌을 선택했을 경우
if selected:

    # 선택한 시즌의 인덱스를 session_state에 저장
    st.session_state.episode_index = options.index(selected)

    # 수집 버튼 생성
    if st.button(
        f"귀멸의 칼날 '{options[st.session_state.episode_index]}' 수집"
    ):

        # main 함수 실행
        if main() == 0:
            st.text("수집된 데이터가 없습니다.")