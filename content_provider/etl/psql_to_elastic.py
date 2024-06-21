import logging.config
import time
from contextlib import closing
from dataclasses import asdict
import argparse

import backoff
import psycopg2
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ElasticConnectionError
from elasticsearch.helpers import bulk
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from dataclasses_storage import FilmWork, Person, Genre
from elastic_schema import schema_movies, schema_persons, schema_genres
from sql_bank import *
from state import JsonFileStorage, State
from config import settings

load_dotenv()
logging.config.fileConfig('logger.conf')


class PostgresExtractor:
    def __init__(self, pg_conn: _connection):
        self.connect = pg_conn

    def extract_timer_and_ids(self, data: list, timer: str):
            if data:
                last_input = data[-1][1].isoformat()
                id = tuple(i[0] for i in data)
                if len(data) == 1:
                    id = tuple([id[0]])
            else:
                last_input = timer
                id = tuple(["00000000-0000-0000-0000-000000000000"])
            return last_input, id

    def extract_modified_data_movies(self,
                                     timer_genres: str,
                                     timer_persons: str,
                                     timer_filmworks: str):
        """Выгрузка измененных данных из PostgreSQL (movies и связанные с ними)"""

        cursor = self.connect.cursor()
        cursor.execute(SQL_LAST_INSERTED_PERSONS, (timer_persons, settings.PERSON_LIMIT))
        data_persons = cursor.fetchall()
        last_input_persons, persons_id = self.extract_timer_and_ids(data_persons, timer_persons)

        cursor.execute(SQL_LAST_INSERTED_GENRES, (timer_genres, settings.GENRE_LIMIT))
        data_genres = cursor.fetchall()
        last_input_genres, genres_id = self.extract_timer_and_ids(data_genres, timer_genres)

        cursor.execute(SQL_LAST_INSERTED_TIME_FILMWORKS, (timer_filmworks, settings.FILMWORK_LIMIT))
        data_filmworks = cursor.fetchall()
        last_input_filmworks, filmworks_id = self.extract_timer_and_ids(data_filmworks, timer_filmworks)

        cursor.execute(ALL_MODIFIED_MOVIES, (persons_id, genres_id, filmworks_id))
        movies_from_postgres = cursor.fetchall()

        return movies_from_postgres, [last_input_genres, last_input_persons, last_input_filmworks]

    def extract_modified_data_persons(self,
                                      timer_persons: str,
                                      timer_filmworks: str):
        """Выгрузка измененных данных из PostgreSQL (persons и связанные с ними)"""

        cursor = self.connect.cursor()
        cursor.execute(SQL_LAST_INSERTED_PERSONS, (timer_persons, settings.PERSON_LIMIT))
        data_persons = cursor.fetchall()
        last_input_persons, persons_id = self.extract_timer_and_ids(data_persons, timer_persons)

        cursor.execute(SQL_LAST_INSERTED_TIME_FILMWORKS, (timer_filmworks, settings.FILMWORK_LIMIT))
        data_filmworks = cursor.fetchall()
        last_input_filmworks, filmworks_id = self.extract_timer_and_ids(data_filmworks, timer_filmworks)

        cursor.execute(ALL_MODIFIED_PERSONS, (filmworks_id, persons_id))
        persons_from_postgres = cursor.fetchall()

        return persons_from_postgres, [last_input_persons, last_input_filmworks]

    def extract_modified_data_genres(self,
                                     timer_genres: str,
                                     timer_filmworks: str):
        """Выгрузка измененных данных из PostgreSQL (genres и связанные с ними)"""

        cursor = self.connect.cursor()
        cursor.execute(SQL_LAST_INSERTED_GENRES, (timer_genres, settings.GENRE_LIMIT))
        data_genres = cursor.fetchall()
        last_input_genres, genres_id = self.extract_timer_and_ids(data_genres, timer_genres)

        cursor.execute(SQL_LAST_INSERTED_TIME_FILMWORKS, (timer_filmworks, settings.FILMWORK_LIMIT))
        data_filmworks = cursor.fetchall()
        last_input_filmworks, filmworks_id = self.extract_timer_and_ids(data_filmworks, timer_filmworks)

        cursor.execute(ALL_MODIFIED_GENRES, (filmworks_id, genres_id))
        genres_from_postgres = cursor.fetchall()

        return genres_from_postgres, [last_input_genres, last_input_filmworks]


class DataTransform:
    def movies_from_postgres_to_elastic(self, rows: list):
        """Подготовка фильмов для вставки в ElasticSearch"""

        def removekey(d: dict, key: str):
            del d[key]
            return d

        data = [removekey(asdict(FilmWork(*movie)), "persons") for movie in rows]
        return data

    def persons_from_postgres_to_elastic(self, rows: list):
        """Подготовка персон для вставки в ElasticSearch"""
        data = [asdict(Person(*person)) for person in rows]
        return data
    
    def genres_from_postgres_to_elastic(self, rows: list):
        """Подготовка жанров для вставки в ElasticSearch"""
        data = [asdict(Genre(*genre)) for genre in rows]
        return data


class ElasticsearchLoader:
    def upload_to_elastic(self, data_for_elastic: list, index_name: str):
        """Вставка данных в ElasticSearch"""
        with Elasticsearch(f'http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}') as es:
            actions = [
                {
                    "_index": index_name,
                    "_id": data["id"],
                    "_source": data,
                    "doc_as_upsert": True
                } for data in data_for_elastic
            ]
            bulk(es, actions)
            logging.info(f"В ElasticSearch обновлены {len(data_for_elastic)} данных в индексе {index_name}")


def postgres_to_elastic_movies(pg_conn: _connection):
    """Основной метод загрузки movies из Postgres в Elastic"""
    while True:
        timer_genres = state.get_state("timer_genres")
        timer_persons = state.get_state("timer_persons")
        timer_filmworks = state.get_state("timer_filmworks")
        postgres_exporter = PostgresExtractor(pg_conn)
        data_from_postgres, timers = postgres_exporter.extract_modified_data_movies(
            timer_genres, timer_persons, timer_filmworks
        )
        transfer = DataTransform()
        all_movies_elastic = transfer.movies_from_postgres_to_elastic(data_from_postgres)
        if all_movies_elastic:
            loader = ElasticsearchLoader()
            loader.upload_to_elastic(all_movies_elastic, 'movies')
            state.set_state("timer_genres", timers[0])
            state.set_state("timer_persons", timers[1])
            state.set_state("timer_filmworks", timers[2])
        else:
            logging.info("Нет данных для обновления")
        time.sleep(settings.RELAX_TIME)


def postgres_to_elastic_persons(pg_conn: _connection):
    """Основной метод загрузки persons из Postgres в Elastic"""
    while True:
        timer_genres = state.get_state("timer_genres")
        timer_persons = state.get_state("timer_persons")
        timer_filmworks = state.get_state("timer_filmworks")
        postgres_exporter = PostgresExtractor(pg_conn)
        data_from_postgres, timers = postgres_exporter.extract_modified_data_persons(
            timer_persons, timer_filmworks
        )
        transfer = DataTransform()
        all_persons_elastic = transfer.persons_from_postgres_to_elastic(data_from_postgres)
        if all_persons_elastic:
            loader = ElasticsearchLoader()
            loader.upload_to_elastic(all_persons_elastic, 'persons')
            state.set_state("timer_persons", timers[0])
            state.set_state("timer_filmworks", timers[1])
        else:
            logging.info("Нет данных для обновления")
        time.sleep(settings.RELAX_TIME)


def postgres_to_elastic_genres(pg_conn: _connection):
    """Основной метод загрузки genres из Postgres в Elastic"""
    while True:
        timer_genres = state.get_state("timer_genres")
        timer_persons = state.get_state("timer_persons")
        timer_filmworks = state.get_state("timer_filmworks")
        postgres_exporter = PostgresExtractor(pg_conn)
        data_from_postgres, timers = postgres_exporter.extract_modified_data_genres(
            timer_genres, timer_filmworks
        )
        transfer = DataTransform()
        all_genres_elastic = transfer.genres_from_postgres_to_elastic(data_from_postgres)
        if all_genres_elastic:
            loader = ElasticsearchLoader()
            loader.upload_to_elastic(all_genres_elastic, 'genres')
            state.set_state("timer_genres", timers[0])
            state.set_state("timer_filmworks", timers[1])
        else:
            logging.info("Нет данных для обновления")
        time.sleep(settings.RELAX_TIME)


def backoff_hdlr(details):
    logging.info(f"backoff_hdlr, {details}")


backoff_etl = backoff.on_exception(backoff.expo, (
                          psycopg2.OperationalError,
                          psycopg2.InterfaceError,
                          ElasticConnectionError
                          ),
                      max_value=10,
                      on_backoff=backoff_hdlr)


@backoff_etl
def run_etl_movies():
    with closing(psycopg2.connect(**settings.dsl, cursor_factory=DictCursor)) as pg_conn:
        postgres_to_elastic_movies(pg_conn)


@backoff_etl
def run_etl_persons():
    with closing(psycopg2.connect(**settings.dsl, cursor_factory=DictCursor)) as pg_conn:
        postgres_to_elastic_persons(pg_conn)


@backoff_etl
def run_etl_genres():
    with closing(psycopg2.connect(**settings.dsl, cursor_factory=DictCursor)) as pg_conn:
        postgres_to_elastic_genres(pg_conn)


def create_schema(index: str, body: str):
    try:
        es.indices.create(index=index, body=body)
        logging.info(f"Индекс {index} создан")
    except:
        logging.info(f"Индекс {index} уже существует")


if __name__ == "__main__":
    storage = JsonFileStorage("state.json")
    state = State(storage)
    state.set_state("timer_genres", settings.TIMER_GENRES)
    state.set_state("timer_persons", settings.TIMER_PERSONS)
    state.set_state("timer_filmworks", settings.TIMER_FILMWORKS)
    es = Elasticsearch(f'http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', type=str, choices=['movies', 'persons', 'genres'], help='тип объекта для загрузки')
    args = parser.parse_args()
    if args.o:
        if args.o == 'movies':
            create_schema("movies", schema_movies)
            run_etl_movies()
        elif args.o == 'persons':
            create_schema("persons", schema_persons)
            run_etl_persons()
        elif args.o == 'genres':
            create_schema("genres", schema_genres)
            run_etl_genres()
    es.transport.close()

