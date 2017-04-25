from aioweb.core.model import Model, mutator
from passlib.handlers.sha2_crypt import sha256_crypt


class AbstractUser(object):

    def is_authenticated(self):
        return False


class User(Model, AbstractUser):

    __guarded__ = ['id']

    @mutator
    def password(self, value):
        #TODO: configurable hash type
        self.set_raw_attribute('password', sha256_crypt.hash(value))

    def can(self, permission):
        pass

    def __str__(self):
        return self.username

