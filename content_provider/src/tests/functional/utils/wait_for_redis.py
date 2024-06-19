import sys
from os.path import dirname, abspath, join
sys.path.append(abspath(join(dirname(__file__), "../../..")))
from helper import backoff_exception
from redis.asyncio import Redis
from tests.functional.settings import test_settings


@backoff_exception
def run():
    redis_client = Redis(host={test_settings.REDIS_HOST}, 
                         port={test_settings.REDIS_PORT})
    if not redis_client.ping():
        raise ValueError('Неверный код ответа')


if __name__ == '__main__':
    run()