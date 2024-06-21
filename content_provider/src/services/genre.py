import pickle
from functools import lru_cache

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.movies import Genre
from redis.asyncio import Redis
from .helper import AsyncCache

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    def __init__(self, elastic: AsyncElasticsearch, cache: AsyncCache):
        self.cache = cache
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Genre | None:
        key = 'genre_id' + genre_id
        genre = await self._genre_from_cache(key)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(key, genre)
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Genre | None:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _genre_from_cache(self, key: str) -> Genre | None:
        data = await self.cache.get(key)
        if not data:
            return None

        return pickle.loads(data)

    async def _put_genre_to_cache(self, key, genre: Genre):
        await self.cache.set(str(key), pickle.dumps(genre), GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def get_all_from_elastic(self) -> list[Genre] | None:
        try:
            docs = await self.elastic.search(index='genres',
                                             size='10000',
                                             filter_path='hits.hits._source',
                                             query={'match_all': {}}
                                             )
            if not docs:
                return None
            all_docs = [doc["_source"] for doc in docs["hits"]["hits"]]
        except NotFoundError:
            return None
        return all_docs

    async def get_all(self) -> list[Genre] | None:
        genres = await self._genre_from_cache('all_genres')
        if not genres:
            genres = await self.get_all_from_elastic()
            if not genres:
                return None
            await self._put_genre_to_cache('all_genres', genres)

        return genres


@lru_cache()
def get_genre_service(
        cache: AsyncCache = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic, cache)
