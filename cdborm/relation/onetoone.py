from cdborm.errors import BadType
from cdborm.relation.relation import Relation


class OneToOne(Relation):

    def assign(self, obj):
        print 'assign', self.parent._get_full_class_name(), self.parent.id
        cls = self.related_class
        if type(obj) == cls:
            self._to_assign = [obj]
        else:
            raise BadType()

    def release(self):
        self._to_release = True

    def __call__(self, database=None):
        data = super(OneToOne, self).__call__(database)
        print 'call', data
        if len(data) == 0:
            return None
        else:
            return data[0]
