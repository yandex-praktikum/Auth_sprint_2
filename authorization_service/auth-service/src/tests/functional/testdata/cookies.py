import pytest_asyncio


@pytest_asyncio.fixture(name='prepare_cookies')
def prepare_cookies():
    async def inner(
            access_token: str = None,
            refresh_token: str = None,
            at_mode: str = 'correct',
            rt_mode: str = 'correct') -> dict:

        cookies = []

        access_token_mods = {
            'correct': f'auth-app-access-key={access_token}',
            'no_token': '',
            'empty_token': 'auth-app-access-key='
        }

        refresh_token_mods = {
            'correct': f'auth-app-refresh-key={refresh_token}',
            'no_token': '',
            'empty_token': 'auth-app-refresh-key='
        }

        at_cookie = access_token_mods.get(at_mode)
        rt_cookie = refresh_token_mods.get(rt_mode)

        cookies.append(at_cookie)
        cookies.append(rt_cookie)

        cookies_dict = {'Cookie': ' ; '.join(cookies)}

        return cookies_dict

    return inner
