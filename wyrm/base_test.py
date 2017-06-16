import importlib
import importlib.util

import unittest

import sys

import yaml

import wyrm.lib
import os

import asyncio

from orator.migrations import Migrator, DatabaseMigrationRepository
from orator import Model

settings = None


def get_package_dir(package):
    return os.path.dirname(importlib.util.find_spec(package).origin)


def get_migration_path(base_dir=None, path_prefix=''):
    return os.path.join(os.getcwd() if base_dir is None else base_dir, path_prefix, 'migrations')


def get_seeders_path(base_dir=None, path_prefix=''):
    return os.path.join(os.getcwd() if base_dir is None else base_dir, path_prefix, 'seeds')


def get_migration_paths(settings):
    try:
        with open(os.path.join(wyrm.lib.dirs(settings, format=["config"]), 'migrations.yml')) as fd:
            config = yaml.load(fd)
    except:
        config = {}

    packages = config.get('packages', {})
    path_prefix = config.get('prefix', '')

    migration_paths = []
    seed_paths = []

    for package in packages:
        package_dir = get_package_dir(package)

        if isinstance(package, dict):
            migration_path = os.path.join(package_dir, packages[package].get('migration',
                                                                             get_migration_path('',
                                                                                                      path_prefix=path_prefix)))
            seed_path = os.path.join(package_dir,
                                     packages[package].get('seeds',
                                                           get_seeders_path('', path_prefix=path_prefix)))
        else:
            migration_path = get_migration_path(package_dir, path_prefix=path_prefix)
            seed_path = get_seeders_path(package_dir, path_prefix=path_prefix)

        if os.path.exists(migration_path):
            migration_paths.append(migration_path)

        if os.path.exists(seed_path):
            seed_paths.append(seed_path)

    for migration_path in config.get('migrations', []):
        if os.path.exists(migration_path):
            migration_paths.append(migration_path)

    for seed_path in config.get('seeds', []):
        if os.path.exists(seed_path):
            seed_paths.append(seed_path)

    return migration_paths, seed_paths


def init():
    os.environ["AIOWEB_ENV"] = "test"
    from aioweb.conf import settings
    wyrm.lib.init_orator(settings)

    resolver = Model.get_connection_resolver()
    repository = DatabaseMigrationRepository(resolver, 'migrations')
    migrator = Migrator(repository, resolver)
    migrator.set_connection("test")

    pretend = False

    if not migrator.repository_exists():
        repository.set_source("test")
        repository.create_repository()

    path = wyrm.lib.dirs(settings, format=["migrations"])

    migration_paths, seed_paths = get_migration_paths(settings)

    migration_paths.append(path)

    #migrator.reset(path, pretend)
    migrator.run(migration_paths, pretend)

    try:
        mod = importlib.import_module('db.seeds.database_seeder')
        seeder = getattr(mod, 'DatabaseSeeder')
        seeder(resolver).run()
    except:
        pass

class AioWebTestCase(unittest.TestCase):
    refresh_db_before_test = True
    start_server = False

    def __init__(self, wtf):
        super().__init__(wtf)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        if self.start_server:
            self.init_server()

    def __del__(self):
        self.loop.run_until_complete(self.app.shutdown())
        self.loop.run_until_complete(self.app.cleanup())
        self.loop.close()

    def refresh_db(self):
        resolver = Model.get_connection_resolver()
        repository = DatabaseMigrationRepository(resolver, 'migrations')
        migrator = Migrator(repository, resolver)
        migrator.set_connection("test")

        pretend = False

        path = wyrm.lib.dirs(settings, format=["migrations"])

        migration_paths, seed_paths = get_migration_paths(settings)

        migration_paths.append(path)

        migrator.reset(migration_paths, pretend)
        migrator.run(migration_paths, pretend)

        try:
            mod = importlib.import_module('db.seeds.database_seeder')
            seeder = getattr(mod, 'DatabaseSeeder')
            seeder(resolver).run()
        except:
            pass

    def init_server(self):
        import aioweb
        import aiohttp.test_utils
        import config.routes as router
        self.app = aioweb.Application(loop=self.loop)
        self.loop.run_until_complete(self.app.setup())
        self.client = aiohttp.test_utils.TestClient(self.app, loop=self.loop)

    def setUp(self):
        if self.refresh_db_before_test:
            self.refresh_db()
        if self.start_server:
            self.loop.run_until_complete(self.client.start_server())

    def tearDown(self):
        if self.start_server:
            self.loop.run_until_complete(self.client.close())
