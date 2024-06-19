import sys
from os.path import dirname, abspath, join
sys.path.append(abspath(join(dirname(__file__), "../../..")))
from helper import backoff_exception
from elasticsearch import Elasticsearch
from tests.functional.settings import test_settings


@backoff_exception
def run():
    hosts = f"http://{test_settings.ELASTIC_HOST}:{test_settings.ELASTIC_PORT}"
    es_client = Elasticsearch(hosts=hosts)
    if not es_client.ping():
        raise ValueError('Неверный код ответа')


if __name__ == '__main__':
    run()
