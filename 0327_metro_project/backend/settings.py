from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  # 공용 설정 PART
  # file_path_env: str
  # my_host: str
  # my_user: str
  # my_pwd: str
  # my_port: str
  # server_host: str
  # server_user: str
  # server_pwd: str
  # server_port: str
  api_key: str

  # 실제 사용 PART
  mariadb_host: str
  mariadb_user: str
  mariadb_password: str
  mariadb_port: str
  mariadb_name: str
  
  mariadb_url: str
  
  mariadb_driver: str
  spark_url: str
  host_ip: str
  jdbc_url: str
  
  file_dir: str

  react_url: str
  
  # 안씀
  hadoop_path: str

  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
  )

settings = Settings()
