import os
import re
from hashlib import sha256

import aiofiles
from aiohttp import web, MultiDict
from aiohttp_jinja2 import render_string
from aiohttp_security import forget, remember
from .models.user_profile import UserProfile
from orator.exceptions.query import QueryException

from .models.user_domain import UserDomain
from framework.auth import authenticate, login_required
from framework.auth.models.user import User
from framework.email import mail_traceback, send_mail
from framework.render import template, render_template
from settings import BASE_DIR


async def login(request):
    await request.post()
    try:
        user = await authenticate(request, request.POST.get('username'), request.POST.get('password'))
    except PermissionError:
        # TODO: ajax
        return render_template('auth/login.html', request, {
                                'form':{
                                    'non_field_errors': 'Wrong password or account is not activated'
                                }})
    except ReferenceError:
        # TODO: ajax
        return render_template('auth/login.html', request, {
                                'form': {
                                    'non_field_errors': 'User does not exists'
                                }})

    if request.user.is_authenticated():
        url = request.app.router['cabinet:cabinet'].url()
        response = web.HTTPFound(url)
        await remember(request, response, str(user.username))
    else:
        url = request.app.router['cabinet:auth_login'].url()
        response = web.HTTPFound(url)
    return response


async def logout(request):
    url = request.app.router['index'].url()
    response = web.HTTPFound(url)
    await forget(request, response)
    return response


@template('cabinet/cabinet.html')
@login_required(login_route='cabinet:auth_login')
async def cabinet(request):
    await request.post()
    profile = UserProfile.where('user_id', request.user.id).first_or_fail()
    return {
        'domains': profile.domains
    }

@template('auth/register.html')
async def register(request):
    try:
        await request.post()
        with request.db.transaction() as t:
            u = User(username=request.POST.get('username'),
                     password=request.POST.get('password'),
                     email=request.POST.get('email'),
                     disabled=True,
                     activation=sha256(("%s%s" % (request.POST.get('username'), request.POST.get('password'))).encode()).hexdigest()
                     )
            u.save()
            p = UserProfile(user_id=u.id)
            p.save()
            try:
                await send_mail(request.app,
                                'noreply@streamedian.com',
                                [u.email],
                                'Streamedian.com account activation',
                                render_string('auth/activation_email.txt', request, {
                                    'site': 'streamedian.com',
                                    'activation_key': u.activation
                                })
                )
            except Exception as e:
                t.rollback()
                raise e

    except QueryException as e:
        field = ''
        err = str(e.previous)
        if err.find('UNIQUE') >= 0:
            field = re.match('.*:\susers.([a-zA-Z_0-9]+)', err).group(1)
            message = "%s is already exists" % field
            return {
                'form': {
                    field: {
                        'errors': message
                    }
                }
            }
        elif err.find('is not unique') >= 0:
            field = re.match('column\s([a-zA-Z_0-9]+)\sis not unique', err).group(1)
            message = "%s is already exists" % field
            return {
                'form': {
                    field: {
                        'errors': message
                    }
                }
            }
        else:
            await mail_traceback(request)
            return {
                'form': {
                    'non_field_errors':'Unknown error'
                }
            }
    except Exception as e:
        await mail_traceback(request)
        return {
            'form': {
                'non_field_errors': 'Unknown error'
            }
        }

    response = render_template('auth/registration_complete.html', request, {})
    return response

async def activate_account(request):
    try:
        u = User.where('activation', request.match_info['key']).first_or_fail()
        u.disabled = False
        u.activation = ''
        u.save()
        url = request.app.router['cabinet:auth_login'].url()
        response = web.HTTPFound(url)
    except:
        response = web.HTTPNotFound()
    return response

@template('cabinet/domains.html')
@login_required(login_route='cabinet:auth_login')
async def get_domains(request):
    return {
        'domains': request.user.domains()
    }

@login_required(login_route='cabinet:auth_login')
async def add_domain(request):
    if request.user.is_authenticated():
        await request.post()
        dom = request.POST.get('domain')
        if dom:
            profile = UserProfile.find(request.user.id)
            await profile.add_domain(dom)
            return web.HTTPCreated()
    else:
        return web.HTTPForbidden()
    return web.HTTPBadRequest()

@login_required(login_route='cabinet:auth_login')
async def remove_domain(request):
    profile = UserProfile.find(request.user.id)
    await profile.remove_domain(request.match_info.get('domain_id'))
    return web.HTTPOk()


async def password_change(request):
    return None

async def password_change_done(request):
    return None


async def get_key(request):
    domain = UserDomain.where('domain', request.match_info.get('domain_id')).first_or_fail()
    resp = domain.as_license_entry()
    return web.Response(
        headers=MultiDict({'Content-Disposition': 'Attachment;filename=wsp.lic'}),
        text=resp)


def restricted_file_view(filename, **kwargs):
    async def file_view(request):
        if request.user.is_authenticated():
            try:
                async with aiofiles.open(os.path.join(BASE_DIR, 'app/core/static/download/', filename), mode='rb') as f:
                    return web.Response(
                        headers=MultiDict({'Content-Disposition': 'Attachment;filename=%s' % filename}),
                        body=await f.read()
                    )
            except:
                return web.HTTPNotFound()
        else:
            return web.HTTPForbidden()
    return file_view


async def do_reset_password(request):
    await request.post()
    await send_mail(request.app,
                  recipients=[request.POST.get('email')],
                  subject='Streamedian.com password reset',
                  body=render_template('auth/password_reset_email.html', request, {
                          'site_name': 'streamedian.com',
                          'domain': request,
                          'protocol': '',
                          'uid': '',
                          'token': ''
                  })
              )

    return web.HTTPFound(request.app.router['cabinet:password_reset_done'].url())

async def password_reset_confirm(request):
    return None


def password_reset_actual(request):
    url = request.app.router['cabinet:password_reset_done'].url()
    return web.HTTPFound(url)