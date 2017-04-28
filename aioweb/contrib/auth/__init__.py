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


def get_user_by_name(login):
    try:
        return USER_MODEL.where_raw('username=?', [login]).first_or_fail()
    except ModelNotFound:
        return None


def get_user_by_id(id):
    return USER_MODEL.where_raw('id=?', [id]).first_or_fail()


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        # TODO: check cache
        user = get_user_by_name(identity)
        if user:
            return user.id
        else:
            return None

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        return USER_MODEL.can(permission)


class AuthError(Exception):
    def __init__(self, reason, *args) -> None:
        super().__init__(reason, *args)
        self.reason = reason

    def __str__(self):
        return self.reason


class AuthValidator(object):

    def __init__(self):
        self.reason = "check failed"

    def validate(self, user):
        return False



async def authenticate(request, username, password, remember=False, validators=tuple()):
    user = get_user_by_name(username)
    if user:
        if sha256_crypt.verify(password, user.password):
            for validator in validators:
                if not validator.validate(user):
                    raise AuthError(validator.reason)
            setattr(user, 'is_authenticated', lambda: True)
            request['just_authenticated'] = True
            setattr(request, 'user', user)
            if remember:
                await remember_user(request)
        else:
            setattr(request, 'user', AbstractUser())
            raise AuthError("Password does not match")
    else:
        setattr(request, 'user', AbstractUser())
        raise AuthError("User not found")

    return user


def check_logged(redirect_to=None):
    async def fn(request, controller, actionName):
        if not request.user.is_authenticated():
            if redirect_to:
                raise web.HTTPFound(redirect_to)
            else:
                raise web.HTTPForbidden(reason='Unauthorized')

    return fn


def check_request_key(request):
    if not REQUEST_KEY in request or type(request[REQUEST_KEY]) != dict:
        request[REQUEST_KEY] = {}


async def remember_user(request):
    check_request_key(request)
    request[REQUEST_KEY]['remember'] = True


async def forget_user(request):
    check_request_key(request)
    request[REQUEST_KEY]['forget'] = True
