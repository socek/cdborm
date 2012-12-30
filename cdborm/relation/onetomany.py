from cdborm.errors import BadType, AlreadyAssigned
from cdborm.relation.relation import Relation, ForeignRelation

class OneToMany(Relation):

    def assign(self, obj, database=None):
        cls = self.related_class
        if type(obj) == cls:
            self.value = obj.id
        else:
            raise BadType()

    def release(self):
        self.value = None

    def __call__(self, database=None):
        cls = self.related_class
        if self.value:
            db = cls._get_database(database)
            return cls.get(self.value, database)
        else:
            return None

class OneToManyList(ForeignRelation):

    def __call__(self, database=None):
        def getIdsOfRelatedObjects(db):
            data = []
            generator = db.get_many(self.index_name, self.parent.id)
            try:
                for element in generator:
                    data.append(element['_id'])
            except TypeError:
                pass
            return data
        def transformIdsToObjects(_ids):
            cls = self.related_class
            data = []
            for _id in _ids:
                data.append(cls.get(_id))
            return data
        #-----------------------------------------------------------------------
        db = self.parent._get_database(database)
        _ids = getIdsOfRelatedObjects(db)
        return transformIdsToObjects(_ids)
