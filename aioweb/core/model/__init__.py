from orator import Model as OratorModel, mutator, accessor

class Model(object):

    __db = None
    __cache_engine = None

    @classmethod
    def set_db(cls, db):
        cls.__db = db

    @property
    def db(self):
        return self.__db

    @classmethod
    def set_cache_engine(cls, cache_engine):
        cls.__cache_engine = cache_engine

    @property
    def cache(self):
        return self.__cache_engine


