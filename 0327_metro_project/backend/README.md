<!-- # ――――― [ 공용 설정 PART ] ――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
# FILE_PATH_ENV=D:\IDE\mini_project\seoul_metro_v2
# MY_HOST=192.168.0.107
# MY_USER=root
# MY_PWD=1234
# MY_PORT=23306
# SERVER_HOST=192.168.0.203
# SERVER_USER=lhs
# SERVER_PWD=lhs
# SERVER_PORT=3306
API_KEY=4b7551556b6e6172393456434e4174
# API_KEY=63656c487777616e3438774645687a


# ――――― [ Database 설정 (SQLAlchemy 및 Spark JDBC 공용) ] ―――――――――――――――――――――――――――――
# MARIADB_HOST=${MY_HOST}
# MARIADB_USER=${MY_USER}
# MARIADB_PASSWORD=${MY_PWD}
# MARIADB_PORT=${MY_PORT}
MARIADB_HOST=192.168.0.107
MARIADB_USER=root
MARIADB_PASSWORD=1234
MARIADB_PORT=23306
MARIADB_NAME=db_metro

# ――――― [ SQLAlchemy용 URL (FastAPI에서 사용) ] ―――――――――――――――――――――――――――――――――――――――
MARIADB_URL=mysql+pymysql://${MARIADB_USER}:${MARIADB_PASSWORD}@${MARIADB_HOST}:${MARIADB_PORT}/${MARIADB_NAME}

# ――――― [ Spark 설정 ] ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
MARIADB_DRIVER=D:\IDE\0327_metro_project\backend\mariadb-java-client-3.5.7.jar
SPARK_URL=spark://${MARIADB_HOST}:7077
HOST_IP=192.168.0.107
JDBC_URL=jdbc:mariadb://${MARIADB_HOST}:${MARIADB_PORT}/${MARIADB_NAME}?sessionVariables=sql_mode='ANSI_QUOTES'


# ――――― [ 데이터 경로 ] ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
FILE_DIR=./data/raw

# ――――― [ HADOOP 경로 ] ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
HADOOP_PATH=D:\IDE\0327_metro_project\backend

# ――――― [ REACT_URL 경로 ] ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
REACT_URL=http://192.168.0.107:5173 # 개인용 -->