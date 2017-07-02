from aiohttp.log import web_logger
from aiohttp_session import setup as setup_session, SimpleCookieStorage
from aiohttp_session.redis_storage import RedisStorage
from aioredis import create_pool
from aiohttp_session.cookie_storage import EncryptedCookieStorage


async def setup(app):
    try:
        app['redis_pool'] = await create_pool(('localhost', 6379))
        setup_session(app, RedisStorage(app['redis_pool']))
    except:
        from cryptography import fernet
        import base64
        web_logger.warn("failed to connect to Redis server. Using simple cookie storage")
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup_session(app, EncryptedCookieStorage(secret_key))

async def shutdown(app):
    if app.get('redis_pool'):
        app['redis_pool'].close()
        await app['redis_pool'].wait_closed()
