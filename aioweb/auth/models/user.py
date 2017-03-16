from orator import Model, mutator
from passlib.handlers.sha2_crypt import sha256_crypt

from aioweb.admin import form


class AbstractUser(object):

    def is_authenticated(self):
        return False


class User(Model, AbstractUser):

    __guarded__ = ['id']

    class Admin:
        # TODO: inline user
        username = form.StringField(required=True)
        password = form.PasswordField(required=True)
        email = form.StringField(required=True)
        is_superuser = form.BooleanField()
        is_staff = form.BooleanField()
        disabled = form.BooleanField()


        __id_field__ = 'user_id'

    @mutator
    def password(self, value):
        self.set_raw_attribute('password', sha256_crypt.hash(value))

    def __str__(self):
        return self.username
