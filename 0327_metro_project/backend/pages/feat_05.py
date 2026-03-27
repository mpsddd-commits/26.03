from fastapi import APIRouter
from settings import settings
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/Feat_05", tags=["Feat_05"])

logger = logging.getLogger("uvicorn")

# ==================================================================
# DB LOAD
# mariadb 데이터 가저오기 위한 spark 읽기 부분
# ==================================================================
def get_mariadb_df(spark, query: str):
  return spark.read.format("jdbc") \
    .option("url", f"{settings.jdbc_url}") \
    .option("dbtable", f"({query}) AS tmp") \
    .option("user", f"{settings.mariadb_user}") \
    .option("password", f"{settings.mariadb_password}") \
    .option("driver", "org.mariadb.jdbc.Driver") \
    .load()


# ===================================
# REQUEST MODEL
# ===================================
class SeasonalityRequest(BaseModel):
  year1: int
  year2: int
  month: int | None = None
  type: str = "전체"


# ============================================================
# feat-05 특정연도와 특정연도의 월별 총 이용객 증감률 데이터 가져오기
# ============================================================

@router.post("/metro_05_1")
async def get_gr_metro_data(req: SeasonalityRequest):
  from main import spark
  if spark is None: return {"status": False, "error": "Spark session not initialized"}

  try:
    year1 = req.year1
    year2 = req.year2
    month = req.month
    type_ = req.type

    type_filter = f"AND `성수기구분` = '{type_}'" if type_ != "전체" else ""

    # ---------------------------------------------------------------------
    # 1. 월별 조회 (메인 차트: 기본 막대 + 증감률 선)
    # ---------------------------------------------------------------------
    if month is None:
      logger.info("월별 누적 데이터 조회")
      
      # [A] 대상 연도(year1) 월별+역별 데이터 (기본 막대)
      # 데이터 양 조절을 위해 이용객 수 상위 역 10개만 예시로 사용 (필요시 조정)
      query1 = f"""
        SELECT `월별`, `역명`, SUM(`총 이용객 수`) as cnt
        FROM feat_05
        WHERE `연도` = {year1} {type_filter}
        GROUP BY `월별`, `역명`
      """
      df1 = get_mariadb_df(spark, query1).toPandas()

      # [B] 비교 연도(year2) 월별 총합 (전체 증감률 계산용)
      query2 = f"""
        SELECT `월별`, SUM(`총 이용객 수`) as total_cnt
        FROM feat_05
        WHERE `연도` = {year2} {type_filter}
        GROUP BY `월별`
      """
      df2 = get_mariadb_df(spark, query2).toPandas()
      prev_total_map = dict(zip(df2['월별'], df2['total_cnt']))

      # 데이터 가공: Nivo 누적 바 구조로 변환
      # { 월: '1월', '강남': 100, '서울역': 80, ..., total: 180, growth_rate: 5.2 }
      raw_stations = df1['역명'].unique().tolist()
      result_monthly = []
      
      # 월별로 데이터 그룹화
      for m in range(1, 13):
        month_str = f"{m}월"
        month_df = df1[df1['월별'] == m]
        
        if month_df.empty and m not in prev_total_map: continue

        entry = {"월": month_str}
        current_month_total = 0
        
        # 역별 데이터 채우기 (keys)
        for _, row in month_df.iterrows():
          st_name = row['역명']
          st_cnt = float(row['cnt'])
          entry[st_name] = st_cnt
          current_month_total += st_cnt
        
        entry['total'] = current_month_total # 툴팁용

        # 증감률 계산 (전체 합계 기준)
        prev_month_total = float(prev_total_map.get(m, 0))
        growth = ((current_month_total - prev_month_total) / prev_month_total * 100) if prev_month_total != 0 else 0
        entry['growth_rate'] = round(growth, 2)
        
        result_monthly.append(entry)

      return {
        "status": True, 
        "monthly": result_monthly, 
        "stationKeys": raw_stations # 프론트에서 keys로 사용
      }

    # ---------------------------------------------------------------------
    # 2. 역별 조회 (클릭 시 하위 차트: 기본 막대)
    # ---------------------------------------------------------------------
    else:
      logger.info(f"{month}월 역별 상세 조회")
      # 기존 로직 유지: year1의 특정 월 역별 TOP 20
      query = f"""
        SELECT `역명` as station, SUM(`총 이용객 수`) as value
        FROM feat_05
        WHERE `연도` = {year1} 
          AND `월별` = {month} {type_filter}
        GROUP BY `역명`
        ORDER BY value DESC
        LIMIT 20
      """
      df = get_mariadb_df(spark, query).toPandas()
      res_stations = df.to_dict(orient="records")
      
      return {"status": True, "stations": res_stations}

  except Exception as e:
    logger.error(str(e))
    return {"status": False, "error": str(e)}