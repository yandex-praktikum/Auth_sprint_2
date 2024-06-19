from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = '127.0.0.1'
    POSTGRES_PORT: str = '5432'
    ELASTIC_PORT: str = '9200'
    ELASTIC_HOST: str = 'localhost'

    PERSON_LIMIT: str = '50'
    GENRE_LIMIT: str = '1'
    FILMWORK_LIMIT: str = '200'
    RELAX_TIME: int = 2

    TIMER_GENRES: str = '2020-06-16T20:14:09.310000+00:00'
    TIMER_PERSONS: str = '2020-06-16T20:14:09.310000+00:00'
    TIMER_FILMWORKS: str = '2020-06-16T20:14:09.310000+00:00'

    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')

    @property
    def dsl(self) -> dict:
        return {
            "dbname": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
            "options": "-c search_path=content"
        }


settings = Settings()
