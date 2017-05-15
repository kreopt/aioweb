from aiohttp import web
from aiohttp.log import web_logger
from aiohttp_security import setup as setup_security, authorized_userid, SessionIdentityPolicy, forget, remember

from aioweb.contrib.auth import DBAuthorizationPolicy, USER_MODEL, get_user_by_id, REQUEST_KEY
from aioweb.contrib.auth.models.user import AbstractUser
from aioweb.modules.db import init_db
from aioweb.util import awaitable


async def make_request_user(request):
    identity = await authorized_userid(request)
    if identity:
        try:
            user = get_user_by_id(identity)
            setattr(user, 'is_authenticated', lambda: True)
            setattr(request, 'user', user)
        except USER_MODEL.ModelNotFound:
            setattr(request, 'user', AbstractUser())
    else:
        setattr(request, 'user', AbstractUser())


async def process_auth(request, response):
    if request.get(REQUEST_KEY):
        if request[REQUEST_KEY].get('remember') and request.user.is_authenticated():
            await remember(request, response, request.user.username)
        if request[REQUEST_KEY].get('forget'):
            await forget(request, response)


async def middleware(app, handler):
    async def middleware_handler(request):
        await make_request_user(request)
        try:
            response = await awaitable(handler(request))
        except web.HTTPException as e:
            await process_auth(request, e)
            raise e
        except Exception as e:
            await process_auth(request, e)
            raise e  # web.HTTPInternalServerError(reason='Unknown error')
        else:
            await process_auth(request, response)
        return response

    return middleware_handler


async def setup(app):
    for requirement in ['db', 'session']:
        if not app.has_module(requirement):
            web_logger.warn("%s module is required for auth module. Skipping" % requirement)

    await init_db(app)
    setup_security(app,
                   SessionIdentityPolicy(),
                   DBAuthorizationPolicy())
