from cdborm.errors import BadType
from cdborm.relation.relation import Relation


class OneToMany(Relation):

    def assign(self, obj):
        cls = self.related_class
        if type(obj) == cls:
            self._to_assign = [obj]
        else:
            raise BadType()

    def release(self, obj=None):
        self._to_release = True

    def __call__(self, database=None):
        data = super(OneToMany, self).__call__(database)
        if len(data) == 0:
            return None
        else:
            return data[0]


class OneToManyList(Relation):
    pass
