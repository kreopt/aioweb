import os

import yaml
from aiohttp.log import web_logger

from aioweb.conf import settings


class ConfigReader(object):
    def __init__(self, file) -> None:
        super().__init__()
        self.config = {}
        try:
            with open(os.path.join(settings.BASE_DIR, file), 'r') as stream:
                self.config = yaml.load(stream)
        except FileNotFoundError:
            web_logger.warn("config file %s not found at path %s" % (file, settings.BASE_DIR))

    def get(self, item, default=None):
        ret = self[item]
        return ret if ret is not None else default

    def __getitem__(self, item):
        parts = item.split('.')
        parts.reverse()
        tree = self.config
        while len(parts):
            if type(tree) == dict:
                part = parts.pop()
                if part in tree:
                    tree = tree[part]
            else:
                return None
        return tree
