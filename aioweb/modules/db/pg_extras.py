import psycopg2.extras


class PGDictNamedtupleCursor(psycopg2.extras.NamedTupleCursor):
    def __getitem__(self, item):
        return getattr(self, item)
