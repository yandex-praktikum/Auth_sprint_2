import sys
from os.path import dirname, abspath, join
sys.path.append(abspath(join(dirname(__file__), "../../..")))
import http
import requests
from helper import backoff_exception
from tests.functional.settings import test_settings


@backoff_exception
def run():
    url = f"http://{test_settings.FASTAPI_HOST}:" \
          f"{test_settings.FASTAPI_PORT}/api/v1/health/check"
    response = requests.get(url)
    if response.status_code != http.HTTPStatus.OK:
        raise ValueError('Неверный код ответа')


if __name__ == '__main__':
    run()
