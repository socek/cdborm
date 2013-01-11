# -*- encoding: utf-8 -*-
from CodernityDB.database import HashIndex


class Index(object):
    elements = []

    def __init__(self, name):
        self.name = name

    def __call__(self, wrapped):
        self.elements.append((wrapped, self.name))
        wrapped._name = self.name
        return wrapped

    @classmethod
    def createAllIndexes(cls, db):
        for indexCls, name in cls.elements:
            index = indexCls(db.path, name)
            db.add_index(index)


@Index('type_index')
class TypeIndex(HashIndex):
    key_format = '20s'

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = self.key_format
        super(TypeIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        val = data.get('_type')
        if val:
            return self.make_key(val), None
        else:
            return None

    def make_key(self, key):
        return key[0:20].ljust(20, '\0')


@Index('LinkLeftIndex')
class LinkLeftIndex(HashIndex):
    key_format = '32s'
    key = 'left'

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = self.key_format
        super(LinkLeftIndex, self).__init__(*args, **kwargs)

    def make_key(self, key):
        try:
            return str(key[0:32].ljust(32, '\0'))
        except TypeError:
            return '\0' * 32

    def make_key_value(self, data):
        val = data.get('_type')
        if val is None or val != 'relation link':
            return None
        else:
            val = self.make_key(data.get(self.key))
            return self.make_key(val), None


@Index('LinkRightIndex')
class LinkRightIndex(LinkLeftIndex):
    custom_header = 'from cdborm.index import LinkLeftIndex'
    key = 'right'