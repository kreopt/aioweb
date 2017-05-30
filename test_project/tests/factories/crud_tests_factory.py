from . import factory
from app.models.crud_test import CrudTest
from orator.orm import Factory

@factory.define(CrudTest)
def crud_tests_factory(faker):
    return {
        "wtf": None, 
    }
