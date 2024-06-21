from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = 'movies'
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    elastic_host: str = '127.0.0.1'
    elastic_port: int = 9200
    model_config = SettingsConfigDict(env_file='../../.env', env_file_encoding='utf-8')


settings = Settings()
