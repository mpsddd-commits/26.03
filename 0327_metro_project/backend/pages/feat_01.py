import logging
from fastapi import APIRouter, HTTPException
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.functions import col, year, month, sum as _sum, regexp_replace, to_date
from pyspark.sql import Window
from sqlalchemy import create_engine, text
import pandas as pd # 결과 처리를 위해 추가
from settings import settings


def get_spark():
    return SparkSession.builder.getOrCreate()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feat_01", tags=["/feat_01"])

# 결과 확인용 DB 엔진
mariadb_engine = create_engine(settings.mariadb_url)

@router.post("/create_table")
def create_table():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS db_metro.feat_01 (
        id INT AUTO_INCREMENT PRIMARY KEY,

        년도 INT NOT NULL,
        월 INT NOT NULL,

        승차인원합계 BIGINT DEFAULT 0,
        하차인원합계 BIGINT DEFAULT 0,

        생성일 DATETIME DEFAULT CURRENT_TIMESTAMP,

        UNIQUE KEY uq_year_month (년도, 월),
        INDEX idx_year_month (년도, 월)
    );
    """

    try:
        with mariadb_engine.begin() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()

        return {"message": "테이블 생성 완료"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data_processing")
def run_spark_feat01():
    try:
        logger.info("🚀 Spark 세션 시작 중...")
        spark = SparkSession.builder \
            .appName("feat_01_api") \
            .config("spark.sql.ansi.enabled", "false") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("WARN") # 너무 많은 로그 방지
        spark.conf.set("spark.sql.ansi.enabled", "false")

        jdbc_url = settings.jdbc_url

        # 1. 데이터 로딩 (CAST 처리로 DATE/INT 변환 에러 방지)
        logger.info("📂 [1/5] MariaDB에서 원본 데이터를 읽어오는 중...")
        raw_query = """
        (SELECT 
            CAST(`날짜` AS CHAR) AS `날짜`, 
            CAST(`구분` AS CHAR) AS `구분`,
            CAST(`05~06` AS CHAR) AS `05~06`, CAST(`06~07` AS CHAR) AS `06~07`,
            CAST(`07~08` AS CHAR) AS `07~08`, CAST(`08~09` AS CHAR) AS `08~09`,
            CAST(`09~10` AS CHAR) AS `09~10`, CAST(`10~11` AS CHAR) AS `10~11`,
            CAST(`11~12` AS CHAR) AS `11~12`, CAST(`12~13` AS CHAR) AS `12~13`,
            CAST(`13~14` AS CHAR) AS `13~14`, CAST(`14~15` AS CHAR) AS `14~15`,
            CAST(`15~16` AS CHAR) AS `15~16`, CAST(`16~17` AS CHAR) AS `16~17`,
            CAST(`17~18` AS CHAR) AS `17~18`, CAST(`18~19` AS CHAR) AS `18~19`,
            CAST(`19~20` AS CHAR) AS `19~20`, CAST(`20~21` AS CHAR) AS `20~21`,
            CAST(`21~22` AS CHAR) AS `21~22`, CAST(`22~23` AS CHAR) AS `22~23`,
            CAST(`23~24` AS CHAR) AS `23~24`, CAST(`24~` AS CHAR) AS `24~`
         FROM seoul_metro 
         WHERE `날짜` REGEXP '^[0-9]') AS safe_feat
        """

        df = spark.read.format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", raw_query) \
            .option("user", settings.mariadb_user) \
            .option("password", settings.mariadb_password) \
            .option("driver", "org.mariadb.jdbc.Driver") \
            .load()

        # 2. 전처리: 날짜 정제 및 행별 합계 계산
        time_cols = [
            "05~06","06~07","07~08","08~09","09~10","10~11","11~12","12~13",
            "13~14","14~15","15~16","16~17","17~18","18~19","19~20","20~21",
            "21~22","22~23","23~24","24~"
        ]

        df = df.withColumn("날짜_fixed", to_date(regexp_replace(col("날짜"), r"[^0-9]", ""), "yyyyMMdd")) \
               .withColumn("년도", year(col("날짜_fixed"))) \
               .withColumn("월", month(col("날짜_fixed")))

        row_total_expr = sum([col(c).cast("long") for c in time_cols])
        df = df.withColumn("행별_합계", row_total_expr)

        # 3. Pivot 처리 (승차/하차 컬럼 분리)
        logger.info("🔄 [3/5] 승차/하차 데이터를 컬럼으로 전환(Pivot) 중...")
        pivot_df = df.groupBy("년도", "월") \
                     .pivot("구분", ["승차", "하차"]) \
                     .agg(_sum("행별_합계")) \
                     .withColumnRenamed("승차", "승차인원합계") \
                     .withColumnRenamed("하차", "하차인원합계") \
                     .na.fill(0)

        # 4. MariaDB feat_01 테이블에 저장
        insert_count = pivot_df.count()
        logger.info(f"💾 [4/5] MariaDB 적재 시작... (예정 건수: {insert_count}건)")

        pivot_df.write.format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", "feat_01") \
            .option("user", settings.mariadb_user) \
            .option("password", settings.mariadb_password) \
            .option("driver", "org.mariadb.jdbc.Driver") \
            .option("quoteIdentifiers", "false") \
            .mode("append") \
            .save()

        # 5. [최종 단계] 적재 후 DB 실시간 개수 확인
        with mariadb_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM feat_01"))
            total_db_count = result.scalar()

        logger.info(f"✅ [5/5] 작업 완료! 현재 feat_01 총 레코드 수: {total_db_count}개")
        
        return {
            "status": "success",
            "inserted_count": insert_count,
            "total_db_count": total_db_count,
            "message": "데이터 집계 및 적재가 완료되었습니다."
        }

    except Exception as e:
        logger.error(f"❌ 작업 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/metro_01_01")
# def get_metro_chart_data(type: str = "전체", year: int = None): # year 파라미터 추가
#     try:
#         spark = get_spark()
#         df = spark.read.format("jdbc") \
#             .option("url", settings.jdbc_url) \
#             .option("dbtable", "feat_01") \
#             .option("user", settings.my_user) \
#             .option("password", settings.my_pwd) \
#             .option("driver", "org.mariadb.jdbc.Driver") \
#             .load()

#         # 1. Drill-down을 위한 필터링 (사용자가 연도를 클릭했을 때)
#         if year:
#             df = df.filter(col("년도") == year)

#         # 2. 구분 필터 (승차/하차/전체)
#         if type == "승차":
#             df = df.withColumn("인원", col("승차인원합계"))
#         elif type == "하차":
#             df = df.withColumn("인원", col("하차인원합계"))
#         else:
#             df = df.withColumn("인원", col("승차인원합계") + col("하차인원합계"))

#         # 3. 데이터 가공 및 정렬
#         # year 파라미터 유무에 따라 label 형식을 다르게 줄 수도 있습니다 (예: 2021년 내부라면 '5월'만 표시 등)
#         chart_df = df.withColumn("label", 
#                                  F.concat_ws("-", col("년도"), F.lpad(col("월"), 2, "0"))) \
#                      .select("label", "인원", "년도", "월") \
#                      .orderBy(col("년도").asc(), col("월").asc())

#         result_data = [row.asDict() for row in chart_df.collect()]
        
#         return {
#             "status": "success",
#             "current_view": "yearly_detail" if year else "overall_trend",
#             "selected_year": year,
#             "data": result_data
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
         
# # [KPI 1] 연간 총 이용객 수
# @router.get("/metro_01_02")
# def get_annual_total(year: int = None):
#     try:
#         spark = get_spark()
        
#         # JDBC 로드 (main에서 설정한 JAR 사용)
#         df = spark.read.format("jdbc") \
#             .option("url", settings.jdbc_url) \
#             .option("dbtable", "feat_01") \
#             .option("user", settings.my_user) \
#             .option("password", settings.my_pwd) \
#             .option("driver", "org.mariadb.jdbc.Driver") \
#             .load()

#         if year:
#             df = df.filter(col("년도") == year)

#         result_df = df.withColumn("total", col("승차인원합계") + col("하차인원합계")) \
#                       .groupBy("년도") \
#                       .agg(_sum("total").alias("annual_total")) \
#                       .orderBy(col("년도").desc())

#         # JSON 변환을 위해 collect()
#         result = [row.asDict() for row in result_df.collect()]
#         return {"status": "success", "data": result}
#     except Exception as e:
#         logger.error(f"Error in metro_01_02: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# # [KPI 2] 연간 성장률 (전년 대비)
# @router.get("/metro_01_03")
# def get_growth_rate(year: int = None):
#     try:
#         spark = get_spark()
#         df = spark.read.format("jdbc") \
#             .option("url", settings.jdbc_url) \
#             .option("dbtable", "feat_01") \
#             .option("user", settings.my_user) \
#             .option("password", settings.my_pwd) \
#             .option("driver", "org.mariadb.jdbc.Driver") \
#             .load()

#         # 1. 윈도우 설정: 월별 파티션, 연도순 정렬
#         window_spec = Window.partitionBy("월").orderBy("년도")
        
#         # 2. 전년 대비 성장률 및 데이터 가공 (전체 대상 계산)
#         processed_df = df.withColumn("total", col("승차인원합계") + col("하차인원합계")) \
#                          .withColumn("prev_total", F.lag("total", 1).over(window_spec)) \
#                          .withColumn("growth_rate", 
#                                      F.round(((col("total") - col("prev_total")) / 
#                                               F.when(col("prev_total") == 0, 1).otherwise(col("prev_total"))) * 100, 2)) \
#                          .na.fill(0, ["growth_rate", "prev_total"])

#         # 3. 필터링 로직: 선택한 연도와 그 1년 전 연도까지 포함
#         if year:
#             # 선택 연도(Year)와 직전 연도(Year - 1)를 모두 가져옴
#             processed_df = processed_df.filter((col("년도") == year) | (col("년도") == year - 1))

#         # 4. 최종 데이터 정렬 (리액트 차트 시각화를 위해 연도/월 순차 정렬)
#         result_df = processed_df.select("년도", "월", "total", "prev_total", "growth_rate") \
#                                 .orderBy(col("년도").asc(), col("월").asc())

#         # 5. JSON 변환
#         result = [row.asDict() for row in result_df.collect()]
        
#         return {
#             "status": "success",
#             "target_year": year,
#             "compare_year": year - 1 if year else None,
#             "data": result,
#             "total_count": len(result)
#         }
#     except Exception as e:
#         logger.error(f"❌ 성장률 및 비교 데이터 조회 오류: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# # [KPI 3] 승하차 비율 균형도
# @router.get("/metro_01_04")
# def get_balance(year: int = None, month: int = None):
#     try:
#         spark = get_spark()
#         df = spark.read.format("jdbc") \
#             .option("url", settings.jdbc_url) \
#             .option("dbtable", "feat_01") \
#             .option("user", settings.my_user) \
#             .option("password", settings.my_pwd) \
#             .option("driver", "org.mariadb.jdbc.Driver") \
#             .load()

#         # 1. 필터링
#         if year: df = df.filter(col("년도") == year)
#         if month: df = df.filter(col("월") == month)

#         # 2. 파이 차트용 비중(%) 및 균형도 계산
#         # 총합이 0인 경우 발생할 수 있는 에러 방지를 위해 total_sum을 먼저 계산
#         result_df = df.withColumn("total_sum", col("승차인원합계") + col("하차인원합계")) \
#                       .withColumn("boarding_pct", 
#                                   F.round((col("승차인원합계") / F.when(col("total_sum") == 0, 1).otherwise(col("total_sum"))) * 100, 2)) \
#                       .withColumn("alighting_pct", 
#                                   F.round((col("하차인원합계") / F.when(col("total_sum") == 0, 1).otherwise(col("total_sum"))) * 100, 2)) \
#                       .withColumn("balance_ratio", 
#                                   F.round((col("승차인원합계") / F.when(col("하차인원합계") == 0, 1).otherwise(col("하차인원합계"))) * 100, 2)) \
#                       .select("년도", "월", "승차인원합계", "하차인원합계", "boarding_pct", "alighting_pct", "balance_ratio") \
#                       .orderBy(col("년도").desc(), col("월").desc())

#         # 3. 결과 반환
#         result = [row.asDict() for row in result_df.collect()]
        
#         return {
#             "status": "success",
#             "chart_type": "pie",
#             "data": result
#         }
#     except Exception as e:
#         logger.error(f"Error in metro_01_04: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/metro_01_total")
def get_metro_01_integrated_analysis(type: str = "전체", year: int = None):
    """
    METRO-01 통합 엔드포인트:
    1. 월별 이용객 추세 (Main Chart)
    2. 연간 총 이용객 (KPI 1)
    3. 전년 대비 성장률 및 비교 데이터 (KPI 2)
    4. 승하차 비중 및 균형도 (KPI 3)
    """
    try:
        spark = get_spark()
        
        # 1. 데이터 로드 (캐싱을 통해 반복 연산 속도 향상)
        df = spark.read.format("jdbc") \
            .option("url", settings.jdbc_url) \
            .option("dbtable", "feat_01") \
            .option("user", settings.mariadb_user) \
            .option("password", settings.mariadb_password) \
            .option("driver", "org.mariadb.jdbc.Driver") \
            .load().cache()

        # --- [데이터 가공 공통 로직] ---
        # 기본 total 계산 (승차+하차)
        df_base = df.withColumn("total", col("승차인원합계") + col("하차인원합계"))

        # --- [1. 메인 차트 데이터: get_metro_chart_data] ---
        chart_df = df_base
        if year:
            chart_df = chart_df.filter(col("년도") == year)
        
        # 구분(type)에 따른 인원 설정
        if type == "승차":
            chart_df = chart_df.withColumn("display_value", col("승차인원합계"))
        elif type == "하차":
            chart_df = chart_df.withColumn("display_value", col("하차인원합계"))
        else:
            chart_df = chart_df.withColumn("display_value", col("total"))

        main_chart_data = chart_df.withColumn("label", F.concat_ws("-", col("년도"), F.lpad(col("월"), 2, "0"))) \
            .select("label", "display_value", "년도", "월") \
            .orderBy(col("년도").asc(), col("월").asc()) \
            .collect()

        # --- [2. KPI 1: 연간 총 이용객 수] ---
        annual_total_df = df_base
        if year:
            annual_total_df = annual_total_df.filter(col("년도") == year)
        
        kpi_annual_total = annual_total_df.groupBy("년도") \
            .agg(F.sum("total").alias("annual_total")) \
            .orderBy(col("년도").desc()).collect()

        # --- [3. KPI 2: 성장률 및 비교 (전년 데이터 포함)] ---
        window_spec = Window.partitionBy("월").orderBy("년도")
        growth_df = df_base.withColumn("prev_total", F.lag("total", 1).over(window_spec)) \
            .withColumn("growth_rate", 
                        F.round(((col("total") - col("prev_total")) / 
                                 F.when(col("prev_total") == 0, 1).otherwise(col("prev_total"))) * 100, 2)) \
            .na.fill(0, ["growth_rate", "prev_total"])

        if year:
            growth_df = growth_df.filter((col("년도") == year) | (col("년도") == year - 1))
        
        kpi_growth_data = growth_df.select("년도", "월", "total", "prev_total", "growth_rate") \
            .orderBy(col("년도").asc(), col("월").asc()).collect()

        # --- [4. KPI 3: 승하차 비중 및 균형도] ---
        balance_df = df_base
        if year:
            balance_df = balance_df.filter(col("년도") == year)
            
        kpi_balance_data = balance_df.withColumn("boarding_pct", 
                                  F.round((col("승차인원합계") / F.when(col("total") == 0, 1).otherwise(col("total"))) * 100, 2)) \
            .withColumn("alighting_pct", 
                                  F.round((col("하차인원합계") / F.when(col("total") == 0, 1).otherwise(col("total"))) * 100, 2)) \
            .withColumn("balance_ratio", 
                                  F.round((col("승차인원합계") / F.when(col("하차인원합계") == 0, 1).otherwise(col("하차인원합계"))) * 100, 2)) \
            .select("년도", "월", "boarding_pct", "alighting_pct", "balance_ratio") \
            .orderBy(col("년도").desc(), col("월").desc()).collect()

        # 5. 캐시 해제 및 최종 반환
        df.unpersist()

        return {
            "status": "success",
            "metadata": {
                "selected_year": year,
                "selected_type": type,
                "view_mode": "drill-down" if year else "overall"
            },
            "main_chart": [row.asDict() for row in main_chart_data],
            "kpi_total": [row.asDict() for row in kpi_annual_total],
            "kpi_growth": [row.asDict() for row in kpi_growth_data],
            "kpi_balance": [row.asDict() for row in kpi_balance_data]
        }

    except Exception as e:
        logger.error(f"❌ METRO-01 통합 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))