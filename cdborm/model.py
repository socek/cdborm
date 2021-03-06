# -*- encoding: utf-8 -*-
from CodernityDB.database import PreconditionsException, IndexException, RecordNotFound, RecordDeleted
from cdborm.errors import BadType, FieldValidationError, CanNotOverwriteRelationVariable, NoDbSelected
from cdborm.fields import Field, IdField, TypeField, TypeVersionField
from cdborm.relation import Relation
from copy import deepcopy, copy


def retrive_rev_and_save(db, data):
    _id = data['_id']
    try:
        dbdata = db.get('id', _id)
        data['_rev'] = dbdata['_rev']
        return db.update(data)
    except (RecordNotFound, RecordDeleted):
        if '_rev' in data:
            data.pop('_rev')
        return db.insert(data)


def update_or_insert(db, data):
    try:
        return db.update(copy(data))
    except (PreconditionsException, IndexException, RecordNotFound, RecordDeleted):
        if '_rev' in data:
            data.pop('_rev')
        return db.insert(data)


class ModelType(type):

    def __init__(cls, name, bases, dct):
        def generate_field_property(name):
            def field_fget(self):
                return self._data[name].value

            def field_fset(self, value):
                self._data[name].value = value
            return property(field_fget, field_fset)

        def generate_relation_property(name):
            def relation_fget(self):
                return self._relations[name]

            def relation_fset_mockable(self, value):
                self._relations[name] = value

            def relation_fset(self, value):
                raise CanNotOverwriteRelationVariable()

            if dct.get('mockable', False):
                return property(relation_fget, relation_fset_mockable)
            else:
                return property(relation_fget, relation_fset)

        cls._field_classes = copy(cls._field_classes)
        cls._relation_classes = copy(cls._relation_classes)
        cls._inherited_relations = copy(cls._inherited_relations)

        for name in cls._inherited_relations:
            setattr(cls, name, generate_relation_property(name))

        for name in dir(cls):
            value = getattr(cls, name)
            if issubclass(value.__class__, Field):
                cls._field_classes[name] = value
                setattr(cls, name, generate_field_property(name))

            if issubclass(value.__class__, Relation):
                cls._relation_classes[name] = value
                setattr(cls, name, generate_relation_property(name))
                cls._inherited_relations.append(name)
        super(ModelType, cls).__init__(name, bases, dct)


class Model(object):
    __metaclass__ = ModelType
    database = None
    _type_version = 1
    cache = {}
    _locked = []
    _field_classes = {}
    _relation_classes = {}
    _inherited_relations = []

    def __init__(self, *args, **kwargs):
        def initVars():
            self._relations = {}
            self._data = {}
            self._relations_cache = None
            self._rev_cache = {}

        def initFields():
            self._data['_id'] = IdField()
            self._data['_type_version'] = TypeVersionField(self)
            self._data['_type'] = TypeField(self)

        def copyFieldsInstances():
            for name, field in self._field_classes.items():
                self._data[name] = deepcopy(field)

            for name, relation in self._relation_classes.items():
                self._relations[name] = deepcopy(relation)
                self._relations[name]._init_with_parent(self)

        def setFields(kwargs):
            def assign_relation_object(name, related_obj):
                self._relations[name].assign(related_obj)

            def init_relation(key, value):
                if type(value) in [list, tuple]:
                    for small_value in value:
                        assign_relation_object(key, small_value)
                else:
                    assign_relation_object(key, value)

            def init_variable(key, value):
                self[key].value = value
            #------------------------------------------------------------------
            for key, value in kwargs.items():
                if key in self._relations:
                    init_relation(key, value)
                else:
                    init_variable(key, value)

        def makeDefaults():
            for key, var in self._data.items():
                var.make_default(self)
        #----------------------------------------------------------------------
        initVars()
        copyFieldsInstances()
        initFields()
        setFields(kwargs)
        makeDefaults()

    def __getitem__(self, key):
        return self._data[key]

    def _to_dict(self, db=None):
        def validateFields():
            for name, var in self._data.items():
                ret = var.validate()
                if not ret[0]:
                    raise FieldValidationError(
                        self._get_full_class_name(), name, ret[1])

        def setType(data, db):
            data['_type'] = self._get_full_class_name()
            data['_type_version'] = self._type_version
            try:
                data['_rev'] = self._rev_cache[id(db)]
            except KeyError:
                pass

        def setData(data):
            for name, var in self._data.items():
                if var.value != None:
                    data[name] = var.to_simple_value()

        def setRelation(data, db):
            for name, var in self._relations.items():
                objects = var(db)
                if objects:
                    if type(objects) == list:
                        data['_relation_' + name] = [obj.id for obj in objects]
                    else:
                        data['_relation_' + name] = objects.id
                else:
                    data['_relation_' + name] = None

        #----------------------------------------------------------------------
        validateFields()
        data = {}
        setData(data)
        if db:
            setType(data, db)
            setRelation(data, db)
        return data

    def save(self, database=None, raw_save=update_or_insert):
        def update_object_from_returned_data(data, db):
            self._rev_cache[id(db)] = data.pop('_rev')
            for name, value in data.items():
                self._data[name].value = value

        def update_own_cache(db):
            if not id(db) in self.cache:
                self.cache[id(db)] = {}
            self.cache[id(db)][self.id] = self

        def save_relation_data(db):
            for name, var in self._relations.items():
                var._on_save(db)
        #----------------------------------------------------------------------
        db = self._get_database(database)
        data = self._to_dict(db)
        returned_data = raw_save(db, data)
        update_object_from_returned_data(returned_data, db)
        update_own_cache(db)
        save_relation_data(db)

    def delete(self, database=None):
        db = self._get_database(database)
        data = self._to_dict(db)
        db.delete(data)
        _id = data['_id']
        self.cache[id(db)].pop(_id)

    def copy_to_db(self, to_db, relation_db=None):
        self.save(to_db, retrive_rev_and_save)
        if relation_db:
            for name, relation in self._relations.items():
                data = relation._get_all_db_elements(relation_db)
                for element in data:
                    data = element['doc']
                    retrive_rev_and_save(to_db, data)

    @property
    def id(self):
        return self['_id'].value

    @classmethod
    def _from_dict_1(cls, data, database):
        def assign_relation(name, value, database):
            # this method makes a 'lock' becouse sometimes the relation make an
            # infinite loop
            if not value in cls._locked:
                cls._locked.append(value)

                related_obj = obj._relations[
                    name].related_class.get(value, database)
                obj._relations[name].assign(related_obj)

                cls._locked.remove(value)

        def make_relation_value(name, value, database):
            if value:
                # get name of relation from value name
                name = name.split('_', 2)[2]
                if type(value) == list:
                    for small_value in value:
                        assign_relation(name, small_value, database)
                else:
                    assign_relation(name, value, database)
        #----------------------------------------------------------------------
        obj = cls()
        if '_dbid' in data:
            _dbid = data.pop('_dbid')
            _rev = data.pop('_rev')
            obj._rev_cache[_dbid] = _rev
        if '_rev' in data:
            data.pop('_rev')
        for name, value in data.items():
            if name.startswith('_relation_'):
                make_relation_value(name, value, database)
            else:
                obj._data[name].from_simple_value(value)
        return obj

    @classmethod
    def from_dict(cls, data, database=None):
        if data['_type'] != cls._get_full_class_name():
            raise BadType()
        return getattr(cls, '_from_dict_' + str(data['_type_version']))(data, database)

    @classmethod
    def _get_database(cls, database=None):
        if database is not None:
            return database
        elif cls.database is not None:
            return cls.database
        else:
            raise NoDbSelected()

    @classmethod
    def _get_full_class_name(cls):
        return cls.__name__

    @classmethod
    def updateCacheFromDatabase(cls, _id, database=None):
        db = cls._get_database(database)
        data = db.get('id', _id)
        data['_dbid'] = id(db)
        element = cls.from_dict(data, db)
        if not id(db) in cls.cache:
            cls.cache[id(db)] = {}
        cls.cache[id(db)][_id] = element

    @classmethod
    def get(cls, _id, database=None):
        def createInCacheIfNessesery(db):
            if not id(db) in cls.cache or not _id in cls.cache[id(db)]:
                cls.updateCacheFromDatabase(_id, db)

        def checkType():
            if cls != type(cls.cache[id(db)][_id]):
                raise BadType()

        def getObjectFromCache(db):
            return cls.cache[id(db)][_id]
        #----------------------------------------------------------------------
        db = cls._get_database(database)
        createInCacheIfNessesery(db)
        checkType()
        return getObjectFromCache(db)

    @classmethod
    def all(cls, database=None):
        def get_all_elements(db):
            from cdborm.index import TypeIndex
            data = []
            for element in db.get_many(TypeIndex._name, cls._get_full_class_name()):
                data.append(cls.get(element['_id'], db))
            return data
        #----------------------------------------------------------------------
        db = cls._get_database(database)
        return get_all_elements(db)

    @classmethod
    def get_class_by_name(cls, name):
        for subcls in Model.__subclasses__():
            if subcls._get_full_class_name() == name:
                return subcls

    @classmethod
    def clear_cache(cls):
        cls.cache.clear()
