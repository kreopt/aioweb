from aiohttp.log import web_logger
from aiohttp_session import setup as setup_session, SimpleCookieStorage
from aiohttp_session.redis_storage import RedisStorage
from aioredis import create_pool


async def setup(app):
    try:
        redis_pool = await create_pool(('localhost', 6379))
        setup_session(app, RedisStorage(redis_pool))
    except:
        web_logger.warn("failed to connect to Redis server. Using simple cookie storage")
        setup_session(app, SimpleCookieStorage())
