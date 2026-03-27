from fastapi import APIRouter
from pyspark.sql import functions as F
from settings import settings

router = APIRouter(prefix="/Feat_04", tags=["Feat_04"])

# ===================================================================================
# 1. 공통 데이터 로드 및 공통 필터링(연도)
# ===================================================================================

def load_data(spark, year: str, on_off: str = "전체"):
  df = spark.read.format("jdbc") \
    .option("url", settings.jdbc_url) \
    .option("driver", "org.mariadb.jdbc.Driver") \
    .option("dbtable", "db_metro.feat_04") \
    .option("user", settings.mariadb_user) \
    .option("password", settings.mariadb_password) \
    .load()

  # ――――― [ 데이터 정제 및 필터링 ] ――――――――――――――――――――――――――――――――――――――――――――――――――――

  # 기본 필터: 연도
  year_filter = (F.col("연도") == int(year))

  # 추가 필터: 구분 (승차/하차) - "전체"가 아닐 경우 필터링 수행
  if on_off != "전체":
    year_filter &= (F.col("구분") == on_off)

  refined_sdf = (df.filter(year_filter)
                .select(
                  "호선", "역명", "구분", "요일명", "요일코드",
                  F.col("합계인원").cast("float"),
                  F.col("평균인원").cast("float"),
                  F.col("합계심야인원").cast("float"),
                ))
  return refined_sdf
  
# ===================================================================================
# 2. 히트맵 데이터 생성 함수
# ===================================================================================

def get_heatmap(spark, year: str, on_off: str):
  refined_sdf = load_data(spark, year, on_off)

  # ――――― [ 호선별/요일별 집계 ] ――――――――――――――――――――――――――――――――――――――――――――――――――――――
  agg_sdf = (refined_sdf.groupBy("호선", "요일명", "요일코드")
             .agg(
                F.sum("합계인원").alias("total_count"),
                F.round(F.avg("평균인원"), 2).alias("avg_count"),
                F.sum("합계심야인원").alias("night_count"),
             )
             .orderBy("호선", "요일코드"))
  
  # ---------------------------------------------------------------------------------
  # SQL 형태
  # SELECT
  #   호선,
  #   요일명,
  #   요일코드,
  #   SUM(합계인원) AS total_count,
  #   ROUND(AVG(평균인원), 2) AS avg_count,
  #   SUM(합계심야인원) AS night_count
  # FROM refined_sdf
  # GROUP BY 호선, 요일명, 요일코드
  # ORDER BY 호선, 요일코드;
  # ---------------------------------------------------------------------------------

  # ――――― [ Pandas 변환 & 결과 return ] ――――――――――――――――――――――――――――――――――――――――――――――
  pdf = agg_sdf.toPandas()
  if pdf.empty:
    return[]
  heatmap_data = []
  lines = pdf["호선"].unique()

  for line in lines:
    line_data = pdf[pdf["호선"] == line]
    data_points = line_data.rename(columns={
      "요일명" : "x",
      "total_count": "y",
      "avg_count": "평균이용객수",
      "night_count": "심야이용객수"
    })[["x", "y", "평균이용객수", "심야이용객수"]].to_dict("records")

    heatmap_data.append({
      "id": line,         # id가 히트맵의 Y축
      "data": data_points
    })

    # -------------------------------------------------------------------------------
    # "data" : [
    #     {
    #       "x": "월요일",    # x축
    #       "y": 1500000,  # y축에서 실제 색상의 밀도를 결정하는 '합계인원'
    #       "평균이용객수": ...,
    #       "심야이용객수": ...,
    #     }
    #   ]
    # -------------------------------------------------------------------------------
  return heatmap_data


# ===================================================================================
# 3. 노선 특성별 분류 함수 (불금/주말/업무 노선 식별)
# ===================================================================================

def get_line(spark, year: str, on_off: str):
  refined_sdf = load_data(spark, year, on_off)
  
  line_sdf = (refined_sdf.groupBy("호선")
              .agg(
                # 불목/불금 : 목,금 심야 인원 비중
                F.sum(F.when(F.col("요일명").isin("목요일", "금요일"), F.col("합계심야인원")).otherwise(0)).alias("심야이용지수"),
                # 주말 특화 : 주말 이용객 합계
                F.sum(F.when(F.col("요일명").isin("토요일", "일요일"), F.col("합계인원")).otherwise(0)).alias("주말이용지수"),
                # 업무 중심 : 평일 대비 주말 인원 비율 계산용
                F.sum(F.when(F.col("요일명").isin("월요일", "화요일", "수요일", "목요일", "금요일"), F.col("합계인원")).otherwise(0)).alias("평일이용량")
              ))
  
  # ---------------------------------------------------------------------------------
  # SQL 형태
  # SELECT
  #   호선,
    
  #   SUM(CASE 
  #       WHEN 요일명 IN ('목요일', '금요일') 
  #       THEN 합계심야인원 
  #       ELSE 0 
  #   END) AS night_score,
  #   SUM(CASE 
  #       WHEN 요일명 IN ('토요일', '일요일') 
  #       THEN 합계인원 
  #       ELSE 0 
  #   END) AS weekend_score,
  #   SUM(CASE 
  #       WHEN 요일명 IN ('월요일','화요일','수요일','목요일','금요일') 
  #       THEN 합계인원 
  #       ELSE 0 
  #   END) AS weekday_total
  # FROM refined_sdf
  # GROUP BY 호선;
  # ---------------------------------------------------------------------------------

  # ――――― [ Pandas 변환 & 결과 return ] ――――――――――――――――――――――――――――――――――――――――――――――
  return line_sdf.toPandas().to_dict(orient="records")


# ===================================================================================
# 4. 클릭 상호작용 : 역별 상세 랭킹 함수
# ===================================================================================

def get_click(spark, year: str, line: str, day_name: str, mode: str, on_off: str):
  refined_sdf = load_data(spark, year, on_off)

  # 정렬 기준 컬럼 설정 (일반 이용객 vs 심야 급증 이용객)
  target = "합계인원" if mode == "total" else "합계심야인원"
  alias_name = "총이용량" if mode == "total" else "심야이용량"

  rank_sdf = (
    refined_sdf
    .filter((F.col("호선") == line) & (F.col("요일명") == day_name))
    .select("역명","구분", F.col(target).alias(alias_name))
    .orderBy(F.desc(F.col(alias_name)))
    .limit(20)
  )
  # ---------------------------------------------------------------------------------
  # SQL 형태
  # SELECT
  #   역명,
  #   합계인원 AS value   -- or 합계심야인원
  # FROM refined_sdf
  # WHERE
  #     호선 = '2호선'
  #     AND 요일명 = '월요일'
  # ORDER BY value DESC
  # LIMIT 10;
  # ---------------------------------------------------------------------------------

  # ――――― [ Pandas 변환 & 결과 return ] ――――――――――――――――――――――――――――――――――――――――――――――
  return rank_sdf.toPandas().to_dict(orient="records")


# ===================================================================================
# 5. API 엔드포인트
# ===================================================================================

# ――――― [ (1) 전체 노선 요일별 히트맵 ] ―――――――――――――――――――――――――――――――――――――――――――――――――
@router.get("/metro_04_1", summary="전체 노선 요일별 히트맵")
async def read_heatmap(year: str, on_off: str = "전체"):
  from main import spark
  if not spark:
    return {"status" : False, "message": "Spark 세션 초기화 실패"}  
  try:
    data = get_heatmap(spark, year, on_off)
    return {
      "status": True,
      "metadata": {"year": year, "on_off": on_off},
      "result": data
    }
  except Exception as e:
    return {"status": False, "error": str(e)}
  
# ――――― [ (2) 노선 특성 분류 ] ―――――――――――――――――――――――――――――――――――――――――――――――――
@router.get("/metro_04_2", summary="노선 특성 분류 데이터")
async def read_line(year: str, on_off: str = "전체"):
  from main import spark
  try:
    data = get_line(spark, year, on_off)
    return {
      "status": True,
      "metadata" : {"year": year, "on_off": on_off},
      "result": data
    }
  except Exception as e:
    return {"status": False, "error": str(e)}

# ――――― [ (3) 히트맵 클릭 시 역별 이용객 랭킹 ] ―――――――――――――――――――――――――――――――――――――――――――――――――
@router.get("/metro_04_3", summary="히트맵 클릭 시 역별 이용객 랭킹(승하차 구분)")
async def read_click(year: str, line: str, day_name: str, mode: str = "total", on_off: str = "전체"):
  # mode: 'total' (전체 합계), 'night' (심야 급증 기준)
  from main import spark
  try:
    data = get_click(spark, year, line, day_name, mode, on_off)
    return {
      "status": True,
      "metadata" : {"year": year, "line": line, "day_name": day_name, "mode": mode, "on_off": on_off},
      "result": data
    }
  except Exception as e:
    return {"status": False, "error": str(e)}