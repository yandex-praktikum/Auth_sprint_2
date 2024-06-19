import pickle
from functools import lru_cache
from pydantic import BaseModel

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.movies import FilmsWithPerson, Person
from redis.asyncio import Redis
from .helper import AsyncCache

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, elastic: AsyncElasticsearch, cache: AsyncCache):
        self.cache = cache
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Person | None:
        key = 'person_id' + person_id
        person = await self._person_from_cache(key)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(key, person)
        return person

    async def _get_person_from_elastic(self, person_id: str) -> Person | None:
        try:
            doc = await self.elastic.get(index='persons', id=person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _person_from_cache(self, key: str) -> Person | list[Person] | None:
        data = await self.cache.get(key)
        if not data:
            return None
        return pickle.loads(data)

    async def _put_person_to_cache(self, key, person: Person):
        await self.cache.set(str(key), pickle.dumps(person), PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _search_person_from_elastic(self, phrase: str, page: int, size: int) -> list[Person] | None:
        try:
            docs = await self.elastic.search(
                index='persons',
                filter_path='hits.hits._source',
                size=size,
                from_=(page-1)*size,
                query={
                    "match": {
                        "full_name": {
                            "query": phrase,
                            "fuzziness": "auto"
                             }
                        }
                    }
            )
            if not docs:
                return None
            all_docs = [doc["_source"] for doc in docs["hits"]["hits"]]
        except NotFoundError:
            return None
        return all_docs

    async def films_with_person(self, person_id: str) -> list[FilmsWithPerson] | None:
        person = await self.get_by_id(person_id)
        if person:
            return person.films
        return None

    async def get_by_search(self, phrase: str, page: int, size: int) -> list[Person] | None:
        key = 'persons_search' + phrase + str(page) + str(size)
        persons = await self._person_from_cache(key)
        if not persons:
            persons = await self._search_person_from_elastic(phrase, page, size)
            if not persons:
                return None
            await self._put_person_to_cache(key, persons)

        return persons


@lru_cache()
def get_person_service(
        cache: AsyncCache = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic, cache)


class Pagination(BaseModel):
    page: int = 1
    size: int = 50