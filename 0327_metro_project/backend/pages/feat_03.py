from fastapi import APIRouter
from pyspark.sql import functions as F
from settings import settings

router = APIRouter(prefix="/Feat_03", tags=["Feat_03"])

# ===================================================================================
# 1. 공통 데이터 로드 및 정제 함수
# ===================================================================================

def get_time_pattern(spark, year: str, station_name: str, day_type: str):
  df = spark.read.format("jdbc") \
  .option("url", settings.jdbc_url) \
  .option("driver", "org.mariadb.jdbc.Driver") \
  .option("dbtable", "db_metro.feat_03") \
  .option("user", settings.mariadb_user) \
  .option("password", settings.mariadb_password) \
  .load()

  # -----------------------------------------------------------------------------------
  # (1) MySQL Connection 방법 - 1
  # -----------------------------------------------------------------------------------

  # ――――― [ 데이터 정제 및 필터링 시도 >>> 실패 ] ――――――――――――――――――――――――――――――――――――――――――――――――――――――
  # - split: '서울역(150)'에서 '('를 기준으로 나누어 앞부분만 취함
  # - trim: 혹시 모를 앞뒤 공백 제거
  # - cast: DB의 DECIMAL 타입을 float으로 변환 (JSON 직렬화 에러 방지)
  
  # target_year = int(year)
  # search_station = f"{station_name.strip()}%"

  # sdf = df.filter(
  #   (F.col("연도") == target_year) & 
  #   (F.col("역명").like(search_station)) & 
  #   (F.col("요일구분").contains(day_type.strip()))
  # )

  # ――――― [ 데이터 정제 및 필터링 시도 >>> 성공 ] ―――――――――――――――――――――――――――――――――――――――――
  refined_sdf = df.withColumn(
    "정제역명", 
    F.trim(F.substring_index(F.col("역명"), "(", 1 ))
  ).filter(
      (F.col("연도") == int(year)) &
      (F.col("정제역명") == station_name.strip()) &
      (F.col("요일구분") == day_type.strip())
    )
  
  # ――――― [ 필요한 컬럼 선택 및 정렬 ] ―――――――――――――――――――――――――――――――――――――――――――――――――――
  result_sdf = refined_sdf.select(
    F.col("시간대").alias("x"),
    F.col("역번호"),
    F.col("구분"),
    F.col("평균인원").cast("float").alias("y"),
    F.col("혼잡도지수").cast("float")
  ).orderBy("x")
  # .orderBy(F.substring(F.col("시간대"), 1, 2).cast("int"))
  # .orderBy("시간대")

  # ――――― [ Pandas 변환 & 결과 return ] ――――――――――――――――――――――――――――――――――――――――――――――
  pdf = result_sdf.toPandas()
  if pdf.empty:
    print(f"데이터 없음: {year}, {station_name}, {day_type}")
    return[]
  return pdf.to_dict(orient="records")

  # -----------------------------------------------------------------------------------
  # (2) MySQL Connection 방법 - 2
  # -----------------------------------------------------------------------------------

  # ――――― [ SQL 사용을 위한 임시 뷰 생성 ] ―――――――――――――――――――――――――――――――――――――――――――――――
  # print(f"✅ 전체 로드된 데이터 건수: {df.count()}")
  # df.createOrReplaceTempView("feat_03_view")

  # # ――――― [ SQL 쿼리 작성 ] ――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
  # safe_station = station_name.replace("'", "''")
  # sql = f"""
  #   select `시간대`, `구분`, `평균인원`, `혼잡도지수`
  #   from (
  #     select *, 
  #       trim(substring_index(`역명`, '(', 1)) as `정제역명` 
  #     from feat_03_view
  #   ) as t
  #   where `연도` = {int(year)}
  #     and `정제역명` = '{safe_station}'
  #     and `요일구분` = '{day_type}'
  #   order by `시간대`
  # """
  # # ――――― [ 쿼리 실행 및 Pandas 변환 ] ―――――――――――――――――――――――――――――――――――――――――――――――――――
  # pdf = spark.sql(sql).toPandas()
  
  # # pdf['평균인원'] = pdf['평균인원'].astype(float)
  # # pdf['혼잡도지수'] = pdf['혼잡도지수'].astype(float)

  # if pdf.empty:
  #   return []

  # return pdf.to_dict(orient="records")


# ===================================================================================
# 2. 정렬 보조 함수
# ===================================================================================

def get_total(item):
   return item["총인원"]


# ===================================================================================
# 3. API 엔드포인트
# ===================================================================================

# # ――――― [ (1-1) 승하차 피크 타임 패턴 비교 (라인 차트용) >>> 폐기 ] ―――――――――――――――――――――
# @router.get("/metro_03_1", summary="시간대별 승하차 패턴")
# async def read_time_pattern(year: str, station_name: str, day_type: str = "평일"):
#   from main import spark
#   if not spark:
#     return {"status" : False, "message": "Spark 세션 초기화 실패"}
#   try:
#     data = get_time_pattern(spark, year, station_name, day_type)
#     return {
#       "status": True,
#       "result": data
#     }
#   except Exception as e:
#     return {"status": False, "error": str(e)}


# ――――― [ (1-2) 승하차 피크 타임 패턴 비교 (다중 선 차트용) ] ―――――――――――――――――――――――――――――――
@router.get("/metro_03_1", summary="승차 vs 하차 시간대별 패턴 비교")
async def read_time_pattern(year: str, station_name: str, day_type: str):
  from main import spark

  # Spark 세션 체크
  if not spark:
    return {"status" : False, "message": "Spark 세션 초기화 실패"}
  
  # 'get_time_pattern' 호출
  try:
    # 함수로부터 List[dict] 데이터 받음 (DB 원본 리스트)
    raw_data = get_time_pattern(spark, year, station_name, day_type)

    if not raw_data:
      return {"status": True, "result": []}
    
    # 프론트엔드 다중 선 차트 형식으로 가공
    chart_data = []
    for g in ["승차", "하차"]:
      # 해당 구분에 맞는 데이터 필터링 후 data 배열 만들기
      points = [
        {"x": d['x'], "y": round(d['y'], 2), "혼잡도지수": d.get("혼잡도지수", 0)}
        for d in raw_data if d["구분"] == g
      ]
      if points:
        chart_data.append({
          "id": g,
          "station_code": raw_data[0].get("역번호", ""),
          "data": points
        })
      
    return {
      "status" : True,
      "metadata" : {"year": year, "station": station_name, "day_type": day_type},
      "result": chart_data
    }
  except Exception as e:
    return {"status": False, "error": str(e)}
  
# ――――― [ (2) 골든 타임 정의 (최대 혼잡 시간대 추출) ] ―――――――――――――――――――――――――――――――
# 해당 역의 하루 중 가장 인원이 많은 시간 TOP 3 정의
@router.get("/metro_03_2", summary="최대 혼잡 시간대(골든 타임) 추출")
async def read_golden_time(year: str, station_name: str, day_type: str):
  from main import spark
  if not spark:
    return {"status" : False, "message": "Spark 세션 초기화 실패"}
  try:
    raw_data = get_time_pattern(spark, year, station_name, day_type)
    if not raw_data:
            return {"status": True, "result": []}
    
    # 시간대별로 승차+하차 인원을 합산
    time_agg = {}
    for d in raw_data:
      t = d["시간대"]
      if t not in time_agg:
        time_agg[t] = {
           "시간대": t, 
           "총인원": 0, 
           "최대혼잡도": 0
        }
      time_agg[t]["총인원"] += d["평균인원"]

      # 혼잡도 → 해당 시간대의 최대값 유지
      if d["혼잡도지수"] > time_agg[t]["최대혼잡도"]:
          time_agg[t]["최대혼잡도"] = d["혼잡도지수"]

    # 합산된 데이터를 인원수 기준 내림차순 정렬 → 상위 3개 추출
    all_time_list = []
    for val in time_agg.values():
       all_time_list.append({
          "시간대": val["시간대"],
          "총인원": round(val["총인원"], 2),
          "최대혼잡도": round(val["최대혼잡도"], 2)
       })
    sorted_list = sorted(all_time_list, key = get_total, reverse = True)
    golden_list = sorted_list[:3]

    return {
        "status": True, 
        "result": golden_list
    }
  except Exception as e:
      return {"status": False, "error": str(e)}
