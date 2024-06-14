import os

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Class to store fastapi project settings.
    """
    model_config = ConfigDict(extra='ignore')
    project_name: str = Field('Auth API', env='API_PROJECT_NAME')
    # Redis
    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    redis_port: int = Field(6380, env='REDIS_PORT')
    # Postgres
    pg_db: str = Field('', env='PG_DB')
    pg_user: str = Field('', env='PG_USER')
    pg_password: str = Field('', env='PG_PASSWORD')
    pg_host: str = Field('127.0.0.1', env='PG_HOST')
    pg_port: int = Field(5433, env='PG_PORT')
    # Logging
    log_format: str = Field('%(asctime)s - %(name)s - %(levelname)s - %(message)s', env='API_LOG_FORMAT')
    log_default_handlers: list = Field(['console', ], env='API_LOG_DEFAULT_HANDLERS')
    console_log_lvl: str = Field('DEBUG', env='API_CONSOLE_LOG_LVL')
    loggers_handlers_log_lvl: str = Field('INFO', env='API_LOGGERS_HANDLERS_LOG')
    unicorn_error_log_lvl: str = Field('INFO', env='API_UNICORN_ERROR_LOG_LVL')
    unicorn_access_log_lvl: str = Field('INFO', env='API_UNICORN_ACCESS_LOG_LVL')
    root_log_lvl: str = Field('INFO', env='API_ROOT_LOG_LVL')
    # JWT token settings
    jwt_secret_key: str = Field(env='JWT_SECRET_KEY')
    jwt_algorithm: str = Field('HS256', env='JWT_ALGORITHM')
    jwt_at_expire_minutes: int = Field(30, env='JWT_ACCESS_TOKEN_EXPIRE_MINUTES')
    jwt_rt_expire_minutes: int = Field(1440, env='JWT_REFRESH_TOKEN_EXPIRE_MINUTES')


settings = Settings(_env_file='../.env', _env_file_encoding='utf-8')
