from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  mariadb_user: str
  mariadb_password: str
  mariadb_host: str
  mariadb_database: str
  mariadb_port: int

  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
  )

settings = Settings()
