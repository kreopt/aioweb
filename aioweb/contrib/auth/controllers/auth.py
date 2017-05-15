import re
from aiohttp import web

import aioweb.core
from aioweb.contrib.auth import authenticate, AuthError, forget_user, redirect_authenticated
from aioweb.contrib.auth.helpers.validators import sub_email_or_phone
from aioweb.core.controller.decorators import default_layout
from aioweb.conf import settings
from aioweb.util import import_controller, awaitable


@default_layout('base.html')
class AuthController(aioweb.core.Controller):
    async def index(self):
        await redirect_authenticated(self.request)
        if hasattr(settings, 'AUTH_INDEX_HANDLER'):
            ctrl, action = getattr(settings, 'AUTH_INDEX_HANDLER').split('#')
            ctrl_class, ctrl_class_name = import_controller(ctrl)
            hdlr = getattr(ctrl_class, action)
            return await awaitable(hdlr(self))

    async def login(self):
        data = await self.request.post()
        try:
            username = sub_email_or_phone(data.get('username', ''))

            await authenticate(self.request, username, data.get('password'), remember=True)
        except AuthError as e:
            if self.request.is_ajax():
                raise web.HTTPForbidden(reason=str(e))
            else:
                self.flash['AUTH_ERROR'] = str(e)
                raise web.HTTPFound(self.url_for('index'))

        await redirect_authenticated(self.request)
        raise web.HTTPForbidden(reason='Unauthenticated')  # This should not happen

    async def logout(self):
        await forget_user(self.request)
        raise web.HTTPFound(getattr(settings, 'AUTH_GUEST_URL', '/'))
