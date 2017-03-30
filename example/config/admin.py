from aioweb.admin import form, register_model
from aioweb.auth import User


class UserAdmin(object):
    # TODO: inline user
    username = form.StringField(required=True)
    password = form.PasswordField(required=True)
    email = form.StringField(required=True)
    is_superuser = form.BooleanField()
    is_staff = form.BooleanField()
    disabled = form.BooleanField()

    __id_field__ = 'user_id'


register_model(User, UserAdmin)
