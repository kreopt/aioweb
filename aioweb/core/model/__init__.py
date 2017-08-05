from orator import *

class Model(object):

    __db = None

    @classmethod
    def set_db(cls, db):
        cls.__db = db

    @property
    def db(self):
        return self.__db


