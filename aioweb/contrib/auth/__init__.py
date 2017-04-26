import importlib

from aiohttp import web
from aiohttp_security.abc import AbstractAuthorizationPolicy
from orator.exceptions.orm import ModelNotFound
from passlib.hash import sha256_crypt

from aioweb.contrib.auth.models.user import User, AbstractUser

try:
    from aioweb.conf import settings

    USER_MODEL = importlib.import_module(settings.AUTH_USER_MODEL)
except ImportError:
    USER_MODEL = User

REQUEST_KEY = 'AIOWEB_AUTH'


def get_user_from_db(login):
    return USER_MODEL.where_raw('username=?', [login]).first_or_fail()


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        # TODO: check cache
        try:
            user = get_user_from_db(identity)
            return user.id
        except ModelNotFound:
            return None

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        return USER_MODEL.can(permission)


async def authenticate(request, username, password, remember=False):
    try:
        user = get_user_from_db(username)
        if sha256_crypt.verify(password, user.password):
            setattr(user, 'is_authenticated', lambda: True)
            request['just_authenticated'] = True
            setattr(request, 'user', user)
            if remember:
                remember_user(request)
        else:
            setattr(request, 'user', AbstractUser())
            raise PermissionError("Password does not match")
    except ModelNotFound as e:
        setattr(request, 'user', AbstractUser())
        raise ReferenceError(e)

    return user


def check_logged(redirect_to=None):
    async def fn(request, controller, actionName):
        if not request.user.is_authenticated():
            if redirect_to:
                raise web.HTTPFound(redirect_to)
            else:
                raise web.HTTPForbidden(reason='Unauthorized')

    return fn


async def remember_user(request):
    if type(request[REQUEST_KEY]) != dict:
        request[REQUEST_KEY] = {}
    request[REQUEST_KEY]['remember'] = True


async def forget_user(request):
    if type(request[REQUEST_KEY]) != dict:
        request[REQUEST_KEY] = {}
    request[REQUEST_KEY]['forget'] = True
