from pyspark.sql import SparkSession
from pyspark.sql.functions import trim, col
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from settings import settings
from fastapi.middleware.cors import CORSMiddleware
import pages.spark_service, \
  pages.seoul_data, \
  pages.feat_01, \
  pages.feat_02, \
  pages.feat_03, \
  pages.feat_04, \
  pages.feat_05
import pandas as pd
import os
import traceback

origins = [ settings.react_url, "http://localhost:5173" ]

app = FastAPI(root_path="/api", title="Seoul Metro API")
# app = FastAPI(title="Seoul Metro API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

spark = None
# mariadb_engine = create_engine(settings.mariadb_url)
mariadb_engine = create_engine(settings.mariadb_url, connect_args={"local_infile": 1})

@app.on_event("startup")
def startup_event():
  global spark
  os.environ["HADOOP_HOME"] = settings.hadoop_path
  os.environ["PATH"] += os.pathsep + os.path.join(settings.hadoop_path, "bin")
  try:
    spark = SparkSession.builder \
      .appName("mySparkApp") \
      .master(settings.spark_url) \
      .config("spark.driver.host", settings.host_ip) \
      .config("spark.driver.bindAddress", "0.0.0.0") \
      .config("spark.driver.port", "10000") \
      .config("spark.blockManager.port", "10001") \
      .config("spark.executor.port", "10002") \
      .config("spark.network.timeout", "800s") \
      .config("spark.rpc.askTimeout", "300s") \
      .config("spark.tcp.retries", "16") \
      .config("spark.cores.max", "2") \
      .config("spark.rpc.message.maxSize", "512") \
      .config("spark.driver.maxResultSize", "2g") \
      .config("spark.shuffle.io.maxRetries", "10") \
      .config("spark.shuffle.io.retryWait", "15s") \
      .config("spark.hadoop.fs.defaultFS", "file:///") \
      .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
      .config("spark.jars.packages", "org.mariadb.jdbc:mariadb-java-client:3.5.7") \
      .getOrCreate()
    print("Spark Session Created Successfully!")
  except Exception as e:
    print(f"Failed to create Spark session: {e}")
  
@app.on_event("shutdown")
def shutdown_event():
  global spark
  try:
    if spark:
      spark.stop()
      print("Spark Session Stopped.")
  except Exception as e:
    print("Spark already stopped or failed:", e)
  # if spark:
  #   spark.stop()

def getDataFrame(file_path):
  try:
    full_path = os.path.join(file_path, "2008.csv")
    df = pd.read_csv(full_path, encoding="utf-8", header=0, thousands=',', quotechar='"', skipinitialspace=True)
    df.columns = df.columns.str.strip()
    return df
  except Exception as e:
    return None

def save(df, table_name):
  try:
    with mariadb_engine.connect() as conn:
      conn.execute(text("TRUNCATE TABLE seoul_metro_temp"))
      conn.commit()
    # ANSI = cp949
    # UTF = utf-8
    df.to_sql(table_name, con=mariadb_engine, if_exists='append', index=False)
    return True
  except Exception as e:
    return False
  
def selectData(df, table_name):
  try:
    # properties = {
    #  "user": settings.db_user, 
    #  "password": settings.db_password, 
    #  "driver": "org.mariadb.jdbc.Driver",
    #  "char.encoding": "utf-8",
    #  "stringtype": "unspecified"
    # }
    # spDf = spark.read.jdbc(url=settings.jdbc_url, table=table_name, properties=properties)
    # spDf = spark.read.csv(settings.file_dir, header=True, inferSchema=True, encoding="utf-8")
    # spDf = spark.read.option("header", "true").option("inferSchema", "true").csv("file:///opt/spark/data/2008.csv")

    # query = text(f"SELECT * FROM {table_name} WHERE 구분 = '승차'")
    # df = pd.read_sql(query, con=mariadb_engine)
    spDf = spark.createDataFrame(df)

    print(spDf.columns)
    print(f"데이터 개수: {spDf.count()}")

    spDf.select("날짜", "역번호", "역명", "구분").show(10, truncate=False)

    # spDf.createOrReplaceTempView(table_name)
    # return spark.sql(f"SELECT `날짜`, `역번호`, `역명`, `구분`, `05~06`, `06~07`, `07~08`, `08~09`, `09~10`, `10~11`, `11~12` FROM {table_name}")
    # selected_df = spDf.select('날짜', '역번호', '역명', '구분', '05~06', '06~07', '07~08', '08~09', '09~10', '10~11', '11~12').filter(trim(col("구분")) == "승차")
    spDf = spDf.filter(trim(col("날짜")) != "날짜")
    selected_df = spDf.filter(trim(col("구분")) == "승차")
    # print(selected_df.columns)
    count = selected_df.count()
    print(f"필터링된 데이터 개수: {count}")

    # selected_df.write.jdbc(url=settings.jdbc_url, table=table_name, mode="append", properties=properties)

    # pdf = selected_df.toPandas()
    # chunk_size = 1000
    # pdf.to_sql(table_name, con=mariadb_engine, if_exists='replace', index=False, chunksize=chunk_size, method='multi')
    # print("데이터 적재 완료!!")

    return selected_df.limit(50).toPandas().to_dict(orient="records")
  except Exception as e:
    print(f"Failed to select data: {e}")
    return None

@app.get("/")
def read_root():
  if not spark:
    return {"status": False, "error": "Spark session not initialized"}
  try:
    df = getDataFrame(settings.file_dir)
    print("데이터 프레임 생성 완료!!")
    table_name = "seoul_metro"
    save(df, table_name)
    print("데이터 적재 완료!!")
    if not df.empty:
      result = selectData(df, table_name)
      print("데이터 프레임 변환 완료!!")
      return {"status": True, "data": result}
  except Exception as e:
    traceback.print_exc()
    return {"status": False, "error": str(e)}


# ================================================
# api라우터 for문 돌리기
# ================================================

apis = [ 
  pages.spark_service.router, 
  pages.seoul_data.router, 
  pages.feat_01.router, 
  pages.feat_02.router,
  pages.feat_03.router,
  pages.feat_04.router, 
  pages.feat_05.router
]
for router in apis:
  app.include_router(router)
  

