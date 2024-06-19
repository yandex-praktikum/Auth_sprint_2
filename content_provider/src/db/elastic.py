from elasticsearch import AsyncElasticsearch

from core.config import settings

es = AsyncElasticsearch(hosts=[f'http://{settings.elastic_host}:{settings.elastic_port}'])


async def get_elastic() -> AsyncElasticsearch:
    return es
