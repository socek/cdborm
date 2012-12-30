from cdborm.errors import BadType, AlreadyAssigned

class Relation(object):
    def __init__(self):
        self.parent = None
        self.value = None

class OneToOne(Relation):
    def __init__(self, class_name, index_name):
        super(OneToOne, self).__init__()
        self.class_name = class_name
        self.index_name = index_name

    def assign(self, obj, database=None):
        from cdborm.model import Model
        cls = Model.get_class_by_name(self.class_name)
        if type(obj) == cls:
            db = self.parent._get_database(database)
            if len(list(db.get_many(self.index_name, obj.id))) > 0:
                raise AlreadyAssigned()
            self.value = obj.id
        else:
            raise BadType()

    def release(self):
        self.value = None

    def __call__(self, database=None):
        from cdborm.model import Model
        cls = Model.get_class_by_name(self.class_name)
        if self.value:
            db = cls._get_database(database)
            return cls.get(self.value, database)
        else:
            return None

class OneToOneForeign(Relation):
    def __init__(self, class_name, index_name):
        super(OneToOneForeign, self).__init__()
        self.index_name = index_name
        self.class_name = class_name

    def __call__(self, database=None):
        from cdborm.model import Model
        def getIdOfRelatedObject(db):
            generator = db.get_many(self.index_name, self.parent.id)
            try:
                all_elements = list(generator)
            except TypeError:
                raise RuntimeError('No element found')
            if len(all_elements) > 0:
                return all_elements[0]['_id']
            else:
                raise RuntimeError('No element found')

        db = self.parent._get_database(database)
        try:
            _id = getIdOfRelatedObject(db)
            cls = Model.get_class_by_name(self.class_name)
            return cls.get(_id)
        except RuntimeError:
            return None
