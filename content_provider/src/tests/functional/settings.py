from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = 'movies'
    ELASTIC_PORT: int = 9200
    ELASTIC_HOST: str = '127.0.0.1'
    FASTAPI_PORT: int = 8000
    FASTAPI_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379
    REDIS_HOST: str = '127.0.0.1'
    GOOD_TOKEN: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWZhOWJmYWMtOGYxMC00ZDMzLWFhODEtOTI2YWUzOTJhZWNlIiwicm9sZXMiOltdLCJpYXQiOjE3MTkwNTg4ODksImV4cCI6MTc1MDU5NDg4OX0.R-SXZCJOr5ITdxzk1PKU0yTPdA7NtCUtb3PROVyxxu8'
    BAD_TOKEN: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWZhOWJmYWMtOGYxMC00ZDMzLWFhODEtOTI2YWUzOTJhZWNlIiwiaWF0IjoxNzE5MDQ5MjU0LCJleHAiOjE3MTkwNTEwNTQsInJvbGVzIjpbXX0.mmsXmUZRmt3bzbq3l9mpz3SJDwgsjWYPMZdADZ3iO9Q'
    model_config = SettingsConfigDict(env_file='../../.env.test', env_file_encoding='utf-8')


test_settings = Settings()
