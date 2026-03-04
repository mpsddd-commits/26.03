# -------------------------------
# 1️⃣ 라이브러리 import
# -------------------------------

import streamlit as st        # 웹 대시보드를 쉽게 만들 수 있는 라이브러리
import pandas as pd           # 데이터 분석용 라이브러리 (DataFrame 사용)
from vega_datasets import data  # Altair에서 자주 쓰는 샘플 데이터 제공
from numpy.random import default_rng as rng  # 난수 생성기
import altair as alt          # 고급 시각화 라이브러리


# -------------------------------
# 2️⃣ 페이지 기본 설정
# -------------------------------

st.set_page_config(page_title="미니미")  
# 브라우저 탭에 표시될 제목 설정


# -------------------------------
# 3️⃣ 페이지 제목 출력
# -------------------------------

st.title("[1] 차트 출력하기")
# 가장 큰 제목 (h1 느낌)


# -------------------------------
# 4️⃣ 데이터 준비
# -------------------------------

source1 = data.barley()
# Vega 샘플 데이터 - 보리 생산량 데이터

source2 = data.cars()
# Vega 샘플 데이터 - 자동차 정보 데이터

df = pd.DataFrame(
    rng(0).standard_normal((20, 3)), 
    columns=["a", "b", "c"]
)
# 난수(정규분포) 20행 3열짜리 데이터 생성
# 컬럼 이름은 a, b, c


# -------------------------------
# 5️⃣ 데이터 테이블 출력 (탭 사용)
# -------------------------------

st.header("1. DataFrame List")
# 중간 제목

data1, data2, data3 = st.tabs([
    "1. Vega Datasets - Barley", 
    "2. Vega Datasets - Cars", 
    "3. 난수 생성 - 20행 3열 배열"
])
# 탭 3개 생성

with data1:
    st.dataframe(source1, use_container_width=True)
    # 보리 데이터 테이블 출력

with data2:
    st.dataframe(source2, use_container_width=True)
    # 자동차 데이터 테이블 출력

with data3:
    st.dataframe(df, use_container_width=True)
    # 난수 데이터 테이블 출력


# -------------------------------
# 6️⃣ 막대 차트 출력
# -------------------------------

st.header("2. Bar Chart - Barley 데이터셋")

st.bar_chart(
    source1,          # 사용할 데이터
    x="year",         # x축: 연도
    y="yield",        # y축: 생산량
    color="site",     # 지역별 색상 구분
    stack=False       # 막대를 겹치지 않고 나란히 표시
)


# -------------------------------
# 7️⃣ 난수 데이터 차트 (라인 / 산점도)
# -------------------------------

st.header("3. 난수 데이터 차트")

tab1, tab2 = st.tabs([
    "Line Chart - 난수 데이터셋", 
    "Scatter Chart - 난수 데이터셋"
])
# 두 개의 탭 생성

with tab1:
    st.line_chart(df)
    # 선 그래프 출력 (a, b, c 컬럼 모두 자동으로 표시)

with tab2:
    st.scatter_chart(df)
    # 산점도 그래프 출력


# -------------------------------
# 8️⃣ Altair 차트 (자동차 데이터)
# -------------------------------

st.header("4. Altair Chart - Cars 데이터셋")

chart = alt.Chart(source2).mark_circle().encode(
    x='Horsepower',          # x축: 마력
    y='Miles_per_Gallon',    # y축: 연비
    color='Origin',          # 원산지별 색상 구분
).interactive()
# interactive() → 확대/축소/드래그 가능


# -------------------------------
# 9️⃣ 테마 비교 출력
# -------------------------------

tab3, tab4 = st.tabs([
    "Streamlit theme (default)", 
    "Altair native theme"
])
# 테마 비교용 탭

with tab3:
    st.altair_chart(
        chart, 
        theme="streamlit",        # Streamlit 기본 테마 적용
        use_container_width=True
    )

with tab4:
    st.altair_chart(
        chart, 
        theme=None,               # Altair 기본 테마 사용
        use_container_width=True
    )