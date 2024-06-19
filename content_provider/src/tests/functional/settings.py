from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = 'movies'
    ELASTIC_PORT: int = 9200
    ELASTIC_HOST: str = '127.0.0.1'
    FASTAPI_PORT: int = 8000
    FASTAPI_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379
    REDIS_HOST: str = '127.0.0.1'
    model_config = SettingsConfigDict(env_file='../../.env.test', env_file_encoding='utf-8')


test_settings = Settings()
