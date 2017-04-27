FLASH_SESSION_KEY = 'AIOWEB_FLASH'


class Flash(object):
    def __init__(self, storage):
        self.storage = storage
        self._tempStorage = {}

    def __getitem__(self, item):
        return self._tempStorage.get(item, self.storage[FLASH_SESSION_KEY].get(item))

    def __setitem__(self, key, value):
        self._tempStorage[key] = value

    def keep(self, key):
        self._tempStorage[key] = self.storage.get(key)

    def sync(self):
        self.storage[FLASH_SESSION_KEY] = self._tempStorage