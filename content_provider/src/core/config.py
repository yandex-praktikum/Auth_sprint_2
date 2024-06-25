from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    service_name: str = Field('fastapi-service', env='API_SERVICE_NAME')
    project_name: str = 'movies'
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    elastic_host: str = '127.0.0.1'
    elastic_port: int = 9200
    jwt_secret_key: str = 'dummy1'
    jwt_algorithm: str = 'dummy2'
    model_config = SettingsConfigDict(env_file='../../.env', env_file_encoding='utf-8')
    # Tracer
    jaeger_enable_tracer: bool = Field(default=False, env='JAEGER_ENABLE_TRACER')
    jaeger_host: str = Field(default='jaeger', env='JAEGER_HOST')
    jaeger_port: int = Field(default=6831, env='JAEGER_PORT')


settings = Settings()
