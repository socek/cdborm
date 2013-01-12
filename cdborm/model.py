# -*- encoding: utf-8 -*-
from CodernityDB.database import PreconditionsException, IndexException
from copy import deepcopy
from cdborm.fields import Field, IdField, RevField, TypeField, TypeVersionField
from cdborm.errors import BadType, FieldValidationError, CanNotOverwriteRelationVariable
from cdborm.relation import Relation

_special_attributes = ['_data', '_type_version', '_get_full_class_name', '_relations']


class Model(object):
    database = None
    _type_version = 1
    cache = {}

    def __init__(self, *args, **kwargs):
        def initVars():
            self._data = {
                '_id': IdField(),
                '_rev': RevField(),
                '_type_version': TypeVersionField(self._type_version),
                '_type': TypeField(self._get_full_class_name()),
            }
            self._relations = {}

        def copyFieldsInstances():
            for name in dir(self):
                value = getattr(self, name)
                if issubclass(value.__class__, Field):
                    self._data[name] = deepcopy(value)
                if issubclass(value.__class__, Relation):
                    self._relations[name] = deepcopy(value)
                    self._relations[name]._init_with_parent(self)

        def setFields():
            for key, value in kwargs.items():
                self[key].value = value
        #-----------------------------------------------------------------------
        initVars()
        copyFieldsInstances()
        setFields()

    def __getattribute__(self, name):
        #we need access to special attributes always
        if name in _special_attributes:
            return super(Model, self).__getattribute__(name)

        #if name in _data dict, then it means we want value from element in _data
        if name in self._data:
            return self._data[name].value
        elif name in self._relations:
            return self._relations[name]
        #else we need normal attribute from instance
        else:
            return super(Model, self).__getattribute__(name)

    def __setattr__(self, name, value):
        def isNameInRelations(name):
            try:
                return name in self._relations
            except AttributeError:
                return False
        #-----------------------------------------------------------------------
        #we need access to special attributes always
        if name in _special_attributes:
            super(Model, self).__setattr__(name, value)

        #if name in _data dict, then it means we want to set value from element in _data
        if name in self._data:
            self._data[name].value = value
        elif isNameInRelations(name):
            raise CanNotOverwriteRelationVariable()
        #else we need normal attribute from instance
        else:
            return super(Model, self).__setattr__(name, value)

    def __getitem__(self, key):
        return self._data[key]

    @property
    def id(self):
        try:
            return self['_id'].value
        except KeyError:
            return None

    def _from_dict_1(self, data):
        for name, value in data.items():
            if name.startswith('_relation_'):
                self._relation[name].value = value
            else:
                self._data[name].value = value

    def _from_dict(self, data):
        if data['_type'] != self._get_full_class_name():
            raise BadType()
        getattr(self, '_from_dict_' + str(data['_type_version']))(data)

    def _to_dict(self):
        def validateFields():
            for name, var in self._data.items():
                ret = var.validate()
                if not ret[0]:
                    raise FieldValidationError(self._get_full_class_name(), name, ret[1])

        def setType(data):
            data['_type'] = self._get_full_class_name()
            data['_type_version'] = self._type_version

        def setData(data):
            for name, var in self._data.items():
                if var.value != None:
                    data[name] = var.value

        def setRelation(data):
            for name, var in self._relations.items():
                data['_relation_' + name] = var.value

        #-----------------------------------------------------------------------
        validateFields()
        data = {}
        setData(data)
        setType(data)
        setRelation(data)
        return data

    def save(self, database=None):
        def insert_or_update(data, db):
            try:
                return db.update(data)
            except (PreconditionsException, IndexException):
                return db.insert(data)

        def update_object_from_returned_data(data):
            for name, value in data.items():
                self._data[name].value = value

        def update_own_cache():
            self.cache[self.id] = self

        def save_relation_data(db):
            for name, var in self._relations.items():
                var._on_save(db)
        #-----------------------------------------------------------------------
        db = self._get_database(database)
        data = self._to_dict()
        returned_data = insert_or_update(data, db)
        update_object_from_returned_data(returned_data)
        update_own_cache()
        save_relation_data(db)

    def delete(self, database=None):
        db = self._get_database(database)
        db.delete(self._to_dict())

    @classmethod
    def _get_database(cls, database=None):
        if database:
            return database
        else:
            return cls.database

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
                raise BadType()

        def getObjectFromCache():
            return cls.cache[_id]
        #-----------------------------------------------------------------------
        db = cls._get_database(database)
        createInCacheIfNessesery(db)
        checkType()
        return getObjectFromCache()

    @classmethod
    def all(cls, database=None):
        def get_all_elements(db):
            data = []
            for element in db.get_many(TypeIndex._name, cls._get_full_class_name()):
                data.append(cls.get(element['_id']))
            return data
        #-----------------------------------------------------------------------
        from cdborm.index import TypeIndex
        db = cls._get_database(database)
        return get_all_elements(db)

    @classmethod
    def get_class_by_name(cls, name):
        for subcls in Model.__subclasses__():
            if subcls._get_full_class_name() == name:
                return subcls
