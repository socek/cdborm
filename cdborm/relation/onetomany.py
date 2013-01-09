from cdborm.errors import BadType
from cdborm.relation.relation import Relation

class OneToMany(Relation):

    def assign(self, obj):
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
            return cls.get(self.value, db)
        else:
            return None