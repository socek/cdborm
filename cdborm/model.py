# -*- encoding: utf-8 -*-
from CodernityDB.database import PreconditionsException, IndexException
from copy import copy

class Model(object):
    database = None
    _type_version = 1
    cache = {}

    def __init__(self, *args, **kwargs):
        def initVars():
            self._data = {}
        def copyFieldsInstances():
            for name in dir(self):
                value = getattr(self, name)
                if issubclass(value.__class__, BaseField):
                    self._data[name] = copy(value)
        def setFields():
            for key, value in kwargs.items():
                self[key].value = value
        #-----------------------------------------------------------------------
        initVars()
        copyFieldsInstances()
        setFields()

    def __getattribute__(self, name):
        #we need access to _data always
        if name in ['_data']:
            return super(Model, self).__getattribute__(name)

        #if name in _data dict, then it means we want value from element in _data
        if name in self._data:
            return self._data[name].value
        #else we need normal attribute from instance
        else:
            return super(Model, self).__getattribute__(name)

    def __setattr__(self, name, value):
        #we need access to _data always
        if name in ['_data']:
            super(Model, self).__setattr__(name, value)

        #if name in _data dict, then it means we want to set value from element in _data
        if name in self._data:
            self._data[name].value = value
        #else we need normal attribute from instance
        else:
            return super(Model, self).__setattr__(name, value)

    def __getitem__(self, key):
        return self._data[key]

    @property
    def id(self):
        return self._id

    def _from_dict_1(self, data):
        for name, value in data.items():
            setattr(self, name, value)

    def _from_dict(self, data):
        if data['_type'] != self._get_full_class_name():
            raise RuntimeError('Wrong type!')
        getattr(self, '_from_dict_' + str(data['_type_version']))(data)

    def _to_dict(self):
        def defaultData():
            data = {
                '_type' : self._get_full_class_name(),
                '_type_version' : self._type_version,
            }
        def initDataIfAlreadySaved(data):
            try:
                data['_id'] = self._id
                data['_rev'] = self._rev
            except AttributeError:
                pass
        def setData(data):
            for name in self._elements:
                try:
                    data[name] = getattr(self, name)
                except AttributeError:
                    data[name] = None
        #-----------------------------------------------------------------------
        data = defaultData()
        initDataIfAlreadySaved(data)
        setData(data)
        return data

    def save(self, database=None):
        def insert_or_update(data, db):
            try:
                return db.update(data)
            except (PreconditionsException, IndexException):
                return db.insert(data)
        def update_object_from_returned_data(data):
            for name, value in data.items():
                setattr(self, name, value)
        def update_own_cache():
            self.cache[self._id] = self
        #-----------------------------------------------------------------------
        db = self._get_database(database)
        data = self._to_dict()
        returned_data = insert_or_update(data, db)
        update_object_from_returned_data(returned_data)
        update_own_cache()

    @classmethod
    def _get_database(cls, database=None):
        if database:
            return database
        else:
            return self.database

    @classmethod
    def _get_full_class_name(cls):
        return cls.__name__

    @classmethod
    def updateCacheFromDatabase(cls, _id, database=None):
        db = cls._get_database(database)
        data = db.get('id', _id)
        element = cls()
        element._from_dict(data)
        cls.cache[_id] = element

    @classmethod
    def get(cls, _id, database=None):
        def createInCacheIfNessesery(db):
            if not _id in cls.cache:
                cls.updateCacheFromDatabase(_id, db)
        def checkType():
            if cls != type(cls.cache[_id]):
                raise RuntimeError('bad type')
        def getObjectFromCache():
            return cls.cache[_id]
        #-----------------------------------------------------------------------
        db = cls._get_database(database)
        createInCacheIfNessesery(db)
        checkType()
        return getObjectFromCache()

    @classmethod
    def all(cls, database=None):
        db = cls._get_database(database)

        data = []
        for element in db.all(cls._get_full_class_name()):
            data.append(cls.get(element['_id']))
        return data
