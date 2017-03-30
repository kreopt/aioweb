import asyncio

from aiohttp import web
from aiohttp_security.abc import AbstractAuthorizationPolicy
from aioweb.util import handler_as_coroutine
from orator.exceptions.orm import ModelNotFound
from passlib.hash import sha256_crypt

from aiohttp_security import setup as setup_security,  authorized_userid
from aiohttp_security import SessionIdentityPolicy
from aiohttp.log import web_logger

import aioweb.core
from aioweb.auth.models.user import User, AbstractUser
from aioweb.db import init_db


def login_required(login_url='/auth/', login_route=''):
    def wrapper(func):
        async def wrapped(p, *args):
            if isinstance(p, aioweb.core.BaseController):
                request = p.request
            else:
                request = p

            if request.user.is_authenticated():
                return await handler_as_coroutine(func)(p, *args)
            else:
                if login_route:
                    url = request.app.router[login_route].url()
                else:
                    url = login_url
                return web.HTTPFound(url)

        return wrapped
    return wrapper

class DBAuthorizationPolicy(AbstractAuthorizationPolicy):

    async def authorized_userid(self, identity):
        try:
            return User.where_raw('username=? and disabled=?', [identity, False]).first_or_fail()
        except ModelNotFound:
            return None

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        return False

async def authenticate(request, username, password):
    try:
        user = User.where_raw('username=? and disabled=?', [username, False]).first_or_fail()
        if sha256_crypt.verify(password, user.password):
            setattr(user, 'is_authenticated', lambda: True)
            # TODO: reset csrf
            setattr(request, 'user', user)
        else:
            setattr(request, 'user', AbstractUser())
            raise PermissionError("Password not match")
    except ModelNotFound as e:
        setattr(request, 'user', AbstractUser())
        raise ReferenceError(e)

    return user

async def make_request_user(request):
    identity = await authorized_userid(request)
    if identity:
        try:
            user = User.where_raw('username=? and disabled=?', [identity.username, False]).first_or_fail()
            setattr(user, 'is_authenticated', lambda: True)
            setattr(request, 'user', user)
        except ModelNotFound:
            setattr(request, 'user', AbstractUser())
    else:
        setattr(request, 'user', AbstractUser())

async def user_to_request(app, handler):
    async def middleware_handler(request):
        await make_request_user(request)
        return await handler(request)
    return middleware_handler


async def setup(app):
    #TODO: requirement as decorator
    for requirement in ['db', 'session']:
        if not app.has_module(requirement):
            web_logger.warn("%s module is required for auth module. Skipping" % requirement)

    await init_db(app)
    setup_security(app,
                   SessionIdentityPolicy(),
                   DBAuthorizationPolicy())
    app.middlewares.append(user_to_request)

