# -*- encoding: utf-8 -*-
from CodernityDB.database import HashIndex

class Index(object):
    elements = []

    def __init__(self, name):
        self.name = name

    def __call__(self, wrapped):
        self.elements.append((wrapped, self.name))
        return wrapped

    @classmethod
    def createAllIndexes(cls, db):
        for indexCls, name in cls.elements:
            index = indexCls(db.path, name)
            db.add_index(index)

class BaseIndex(HashIndex):
    custom_header = 'from cdborm.index import BaseIndex'
    key_format = '20s'
    key = None
    relation_key = None

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = self.key_format
        super(BaseIndex, self).__init__(*args, **kwargs)

    def _key(self):
        if self.key:
            return self.key
        elif self.relation_key:
            return '_relation_' + self.relation_key
        else:
            return None

    def make_key_value(self, data):
        val = data.get('_type')
        if val is None or val != self.clsName:
            return None
        else:
            if self._key():
                val = self.make_key(data.get(self._key()))
                return self.make_key(val), None
            else:
                return self.make_key(val), None

        return self.make_key(val), None

    def make_key(self, key):
        return str(key[0:20].ljust(20, '\0'))
