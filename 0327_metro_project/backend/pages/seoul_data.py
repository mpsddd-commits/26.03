from fastapi import APIRouter
import pandas as pd
import requests
from sqlalchemy import create_engine, text
from settings import settings


router = APIRouter(prefix="/spark_service", tags=["1. 원천데이터 적재"])
mariadb_engine = create_engine(settings.mariadb_url, connect_args={"local_infile": 1})

# ==============================
# 시간 컬럼 정규화 (핵심 수정)
# ==============================

def fetch_data():
  all_data = []

  for start in range(1, 5000, 1000):
    end = start + 999
    url = f"http://openapi.seoul.go.kr:8088/{settings.api_key}/json/SearchSTNBySubwayLineInfo/{start}/{end}"
    
    res = requests.get(url).json()

    try:
      rows = res['SearchSTNBySubwayLineInfo']['row']
      all_data.extend(rows)
    except:
      break

  df = pd.DataFrame(all_data)

  # 컬럼명 DB 맞춤 변환
  df = df.rename(columns={
    'STATION_CD': '역번호',
    'STATION_NM': '역명',
    'LINE_NUM': '호선',
    'FR_CODE': '외부코드'
  })
  
  # 역번호가 0012이거나 0001이면 유지하고 0123인 경우에만 0을 제외
  df['역번호'] = df['역번호'].astype(str).apply(
    lambda x: x[1:] if len(x) == 4 and x.startswith('0') and x[1] != '0' else x
  )

  # 필요한 컬럼만 (순서 중요)
  df = df[
    [
      '역번호',
      '역명',
      '호선',
      '외부코드'
    ]
  ]

  # 공백 처리
  df = df.replace('', None)

  return df


def get_seoul_data():
  df = fetch_data()
  mariadb_engine = create_engine(settings.mariadb_url)

  with mariadb_engine.connect() as conn:
    # 기존 데이터 삭제
    conn.execute(text("TRUNCATE TABLE metro_line"))

    # 데이터 적재
    df.to_sql(
      name='metro_line',
      con=conn,
      if_exists='append',
      index=False
    )
    conn.commit()

  print(f"총 {len(df)}건 적재 완료")

  return len(df)


# ================================================
# 서울 열린데이터 광장의 메트로 라인 공공 데이터 받아오기
# ================================================
@router.post("/sync_line")
def sync_line_data():
  try:
    sata = get_seoul_data()

    return {"status": True, "message": f"총 {sata}건 데이터 적재 완료"}

  except Exception as e:
    return {"status": False, "error": str(e)}