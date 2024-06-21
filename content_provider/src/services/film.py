from functools import lru_cache
from typing import Optional, List
import pickle
import logging
from pydantic import BaseModel

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, Query
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.movies import Film
from .helper import AsyncCache

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, elastic: AsyncElasticsearch, cache: AsyncCache):
        self.cache = cache
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        key = self.cache_key('film_get_by_id', film_id)
        film = await self._film_from_cache(film_id) # TODO: update key
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(key, film)
        return film

    async def get(self, genre: str, title: str, page: int, size: int) -> Optional[List[Film]]:
        key = self.cache_key('film_get', genre, title, page, size)
        films = await self._films_from_cache(key)
        if not films:
            films = await self._get_films_from_elastic(genre, title, page, size)
            if not films:
                return None
            await self._put_films_to_cache(key, films)
        return films

    async def get_by_search(self, phrase: str, page: int, size: int) -> Optional[List[Film]]:
        key = self.cache_key('film_get_by_search', phrase, page, size)
        films = await self._films_from_cache(key)
        if not films:
            films = await self._search_films_from_elastic(phrase, page, size)
            if not films:
                return None
            await self._put_films_to_cache(key, films)
        return films

    async def get_all_from_elastic(self) -> list[Film] | None:
        try:
            docs = await self.elastic.search(index='movies',
                                             size='10000',
                                             filter_path='hits.hits._source',
                                             query={'match_all': {}}
                                             )
            if not docs:
                return None
            res: List[Film] = []
            for doc in docs['hits']['hits']:
                film = await self._film_doc_to_model(doc)
                res.append(film)
            return res
        except NotFoundError:
            return None

    async def get_all(self) -> list[Film] | None:
        key = 'all_films'
        films = await self._films_from_cache(key)
        if not films:
            films = await self.get_all_from_elastic()
            if not films:
                return None
            await self._put_films_to_cache(key, films)

        return films

    async def _search_films_from_elastic(self, phrase: str, page: int, size: int) -> Optional[List[Film]]:
        try:
            docs = await self.elastic.search(
                index='movies',
                filter_path='hits.hits._source',
                size=size,
                from_=(page-1)*size,
                body={
                    "query": {
                        "bool": {
                            "must": [{ "match": { "title": phrase } },]
                            }
                        }
                    }
            )
            if not docs:
                return None
            res: List[Film] = []
            for doc in docs['hits']['hits']:
                film = await self._film_doc_to_model(doc)
                res.append(film)
            return res
        except NotFoundError:
            return None

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return await self._film_doc_to_model(doc)

    async def _film_doc_to_model(self, doc) -> Film:
        _doc = doc['_source'].copy()

        if 'directors' in _doc:
            _directors = [{'uuid': d['id'], 'full_name': d['name'], 'films': []} for d in _doc['directors']]
        else:
            _directors = []
        _doc['directors'] = _directors

        if 'writers' in _doc:
            _writers = [{'uuid': w['id'], 'full_name': w['name'], 'films': []} for w in _doc['writers']]
        else:
            _writers = []
        _doc['writers'] = _writers

        if 'actors' in _doc:
            _actors = [{'uuid': a['id'], 'full_name': a['name'], 'films': []} for a in _doc['actors']]
        else:
            _actors = []
        _doc['actors'] = _actors
        
        return Film(**_doc)

    async def _get_films_from_elastic(
            self, 
            genre: str = None, 
            title: str = None, 
            page: int = 1, 
            size: int = 50
        ):
        try:
            if genre or title:
                cond = []
                if genre:
                    cond.append(
                        { "match": { "genres": genre } }
                    )
                if title:
                    cond.append(
                        { "match": { "title": title } }
                    )
                query = {
                    "query": {
                        "bool": {
                            "must": cond
                            }
                        }
                    }
                docs = await self.elastic.search(
                    index='movies', 
                    filter_path='hits.hits._source',
                    size=size,
                    from_=(page-1)*size,
                    body=query
                )
            else:
                docs = await self.elastic.search(
                    index='movies',                    
                    filter_path='hits.hits._source',
                    size=size,
                    from_=(page-1)*size
                )  
        except NotFoundError:
            return None

        res: List[Film] = []
        if 'hits' in docs and 'hits' in docs['hits']:
            for doc in docs['hits']['hits']:
                film = await self._film_doc_to_model(doc)
                res.append(film)
        return res

    async def _film_from_cache(self, key: str) -> Optional[Film]:
        data = await self.cache.get(key)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    async def _films_from_cache(self, key: str) -> Optional[List[Film]]:
        data = await self.cache.get(key)
        if not data:
            return None
        return pickle.loads(data)

    async def _put_film_to_cache(self, key: str, film: Film):  # TODO: update key
        await self.cache.set(key, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _put_films_to_cache(self, key: str, films: List[Film]):  # TODO: update key
        await self.cache.set(key, pickle.dumps(films), FILM_CACHE_EXPIRE_IN_SECONDS)

    def cache_key(self, key_base:str, *args):
        res = key_base
        for arg in args:
            if arg is not None:
                res += str(arg)
        return res

@lru_cache()
def get_film_service(
        cache: AsyncCache = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic, cache)

class Pagination(BaseModel):
    page: int = 1
    size: int = 50

