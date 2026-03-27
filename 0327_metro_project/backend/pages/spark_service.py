from fastapi import APIRouter
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, to_date, lit, when, dayofweek, trim, substring
from sqlalchemy import create_engine, text
from settings import settings
import pandas as pd
import os
import re

router = APIRouter(prefix="/spark_service", tags=["1. 원천데이터 적재"])
mariadb_engine = create_engine(settings.mariadb_url, connect_args={"local_infile": 1})

# ==============================
# 시간 컬럼 정규화 (핵심 수정)
# ==============================
def normalize_time_col(col_name: str):
  c = str(col_name).strip().replace(" ", "")

  # -----------------------------
  # 이전 / 이후 먼저 처리
  # -----------------------------
  if "이전" in c:
    return "05~06"

  if "이후" in c:
    nums = re.findall(r"\d{1,2}", c)
    if nums:
      hour = int(nums[0])
      if hour == 23:
        return "23~24"
      if hour == 24:
        return "24~"
    return "24~"
  
  # ---------------------------------
  # 핵심: 시간 추출을 "정확히 2개"만 사용
  # ---------------------------------
  nums = re.findall(r"\d{1,2}", c)

  if len(nums) >= 2:
    start = int(nums[0])
    end = int(nums[1])

    # -----------------------------
    # 00~01 → 24~
    # -----------------------------
    if start == 0 and end == 1:
      return "24~"

    return f"{start:02d}~{end:02d}"

  return c


# ==============================
# Spark 변환
# ==============================
def spark_transform(pdf, spark):

  # -----------------------------
  # 1. Pandas 전처리
  # -----------------------------
  pdf.columns = [normalize_time_col(c) for c in pdf.columns]

  # 핵심: 중복 컬럼 제거
  pdf = pdf.loc[:, ~pd.Index(pdf.columns).duplicated()]

  # 문자열 정리
  if "날짜" in pdf.columns:
    pdf["날짜"] = pdf["날짜"].astype(str).str.strip()

  if "역명" in pdf.columns:
    pdf["역명"] = pdf["역명"].astype(str).str.strip()

  # -----------------------------
  # 2. Spark 변환
  # -----------------------------
  df = spark.createDataFrame(pdf)

  # -----------------------------
  # 구분 컬럼 처리
  # -----------------------------
  gu_cols = [c for c in df.columns if c.startswith("구분")]
  main_gu = gu_cols[-1]

  df = df.drop(*[c for c in gu_cols if c != main_gu])

  if main_gu != "구분":
    df = df.withColumnRenamed(main_gu, "구분")

  df = df.withColumn("구분", trim(col("구분")))

  df = df.withColumn(
    "구분",
    when(col("구분").contains("승"), "승차")
    .when(col("구분").contains("하"), "하차")
  )

  # -----------------------------
  # 날짜 처리
  # -----------------------------
  df = df.withColumn("날짜", trim(col("날짜")))
  df = df.withColumn("날짜", substring(col("날짜"), 1, 10))
  df = df.withColumn("날짜", to_date(col("날짜"), "yyyy-MM-dd"))

  df = df.withColumn("요일", (dayofweek(col("날짜")) + 5) % 7)

  # -----------------------------
  # 숫자 컬럼 처리
  # -----------------------------
  for c in df.columns:
    if "~" in c:
      df = df.withColumn(
        c,
        regexp_replace(col(c).cast("string"), ",", "").cast("int")
      )

  # -----------------------------
  # 누락 컬럼 보정동
  # -----------------------------
  # target_columns 경우 최조 별도 독립적으로 선언했으나, 
  # 여기서만 사용중이라 여기로 이동
  target_columns = [
    "날짜", "요일", "역번호", "역명", "구분",
    "05~06","06~07","07~08","08~09","09~10",
    "10~11","11~12","12~13","13~14","14~15",
    "15~16","16~17","17~18","18~19","19~20",
    "20~21","21~22","22~23","23~24","24~"
  ]
  # 보정 진행하는 곳
  for c in target_columns:
    if c not in df.columns:
      df = df.withColumn(c, lit(0))

  # -----------------------------
  # 컬럼 정렬
  # -----------------------------
  df = df.select(target_columns)

  return df.toPandas()


# ==============================
# Chunk 기반 처리
# ==============================
def process_large_csv(file_path, spark_instance, chunk_size=10000):
  # ------------------------------------------------------------
  # work 폴더에 존재하는 CSV파일 정재 및 적제 시작 부분
  # 여기서 '_clean.csv' 파일을 생성.....
  # ------------------------------------------------------------
  output_file = file_path.replace(".csv", "_clean.csv")

  if os.path.exists(output_file):
    os.remove(output_file)

  chunk_iter = pd.read_csv(
    file_path,
    chunksize=chunk_size,
    encoding="utf-8",
    thousands=",",
    quotechar='"',
    skipinitialspace=True
  )

  for i, chunk in enumerate(chunk_iter):
    print(f"chunk 처리중: {i}")

    try:
      # spark_instance 전달
      result_pdf = spark_transform(chunk, spark_instance)
      # append 저장
      result_pdf.to_csv(
        output_file,
        mode='a',
        header=not os.path.exists(output_file),
        index=False,
        encoding="utf-8"
      )

    except Exception as e:
      print(f"chunk 실패: {i} / {e}")

  return output_file

# ==============================
# DB 적재
# ==============================
def sync_metro_to_db(conn, file_path):
  file_path = file_path.replace("\\", "/")
  sql = f"""
  LOAD DATA LOCAL INFILE '{file_path}'
  IGNORE
  INTO TABLE db_metro.seoul_metro
  CHARACTER SET utf8
  FIELDS TERMINATED BY ','
  OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\\n'
  IGNORE 1 LINES
  (
    @날짜, @요일, @역번호, @역명, @구분,
    @v05,@v06,@v07,@v08,@v09,
    @v10,@v11,@v12,@v13,@v14,
    @v15,@v16,@v17,@v18,@v19,
    @v20,@v21,@v22,@v23,@v24
  )
  SET
    날짜 = NULLIF(STR_TO_DATE(@날짜, '%Y-%m-%d'), '0000-00-00'),
    요일 = NULLIF(@요일, ''),
    역번호 = NULLIF(@역번호, ''),
    역명 = NULLIF(@역명, ''),
    구분 = NULLIF(@구분, ''),
    `05~06`=@v05, `06~07`=@v06, `07~08`=@v07,
    `08~09`=@v08, `09~10`=@v09, `10~11`=@v10,
    `11~12`=@v11, `12~13`=@v12, `13~14`=@v13,
    `14~15`=@v14, `15~16`=@v15, `16~17`=@v16,
    `17~18`=@v17, `18~19`=@v18, `19~20`=@v19,
    `20~21`=@v20, `21~22`=@v21, `22~23`=@v22,
    `23~24`=@v23, `24~`=@v24;
  """
  conn.execute(text(sql))



# ==============================
# 적재 API
# ==============================
@router.post("/sync_metro")
def sync_metro_data():
  from main import spark

  if spark is None:
    return {
      "status": False, 
      "error": "Spark session is not initialized. Please wait for startup."
    }
  
  try:
    # engine = create_engine(
    #   settings.mariadb_url,
    #   connect_args={"local_infile": 1}
    # )
    
    folder_path = settings.file_dir

    # --------------------------------------------------------------
    # 자동 commit
    # --------------------------------------------------------------
    with mariadb_engine.begin() as conn:
      # ------------------------------------------------------------
      # DB의 전 데이터 삭제하는 SQL이므로 전체 데이터 적제 시에만 주석 해제
      # 일부 데이터만 적제 시 미사용
      # ------------------------------------------------------------
      # conn.execute(text("TRUNCATE TABLE db_metro.seoul_metro"))


      # ------------------------------------------------------------
      # work 폴더에 존재하는 CSV파일 정재 및 적제 시작 부분
      # 여기서 '_clean'으로 끝나는 파일이 아닌 .csv 파일만 바라봄
      # ------------------------------------------------------------
      for file in os.listdir(folder_path):
        if file.endswith(".csv") and "_clean" not in file:
          file_path = os.path.join(folder_path, file)

          try:
            print(f"정제 처리중: {file}")

            # pandas의 chunk 기반 데이터 전달(하나의 CSV를 만번씩 전달 진행) 
            # spark 기반 정제(만번씩 전달 받아서 정제 진행)
            # 즉, 원본 CSV 파일의 데이터를 확인하여 
            # 만번씩 정재된 데이터를 '_clean.csv' 파일에 저장 
            # 핵심: 초기화된 spark 객체를 인자로 넘겨줍니다.
            clean_file = process_large_csv(file_path, spark, 10000)

            # DB 적재
            # 최종 정제가 완료된 '_clean.csv' 파일을 이용하여 DB에 적재
            sync_metro_to_db(conn, clean_file)

            print(f"정제 처리완료: {file}")
          except Exception as e:
            print(f"실패: {file} / {e}")

    return {"status": True, "message": "데이터 적재 완료"}

  except Exception as e:
    return {"status": False, "error": str(e)}