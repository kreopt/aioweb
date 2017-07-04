import importlib

from aiohttp.log import web_logger
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage
from aioredis import create_pool
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from aioweb.conf import settings


async def setup(app):
    try:
        storage = None
        if hasattr(settings, 'SESSION_STORAGE'):
            try:
                mod = importlib.import_module(settings.SESSION_STORAGE)
                storage = await getattr(mod, 'make_storage')(app)
            except:
                web_logger.warn(
                    "failed to setup {} storage. Using simple cookie storage".format(settings.SESSION_STORAGE))
        if not storage:
            app['redis_pool'] = await create_pool(('localhost', 6379))
            storage = RedisStorage(app['redis_pool'])
        setup_session(app, storage)
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
