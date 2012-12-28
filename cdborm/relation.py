from cdborm.errors import BadType
class Relation(object): pass

class OneToOne(Relation):

    def __init__(self, object_type):
        self.object_type = object_type
        self._value = None

    def assign(self, obj):
        if type(obj) == self.object_type:
            self._value = obj.id
        else:
            raise BadType()

    def release(self):
        self._value = None

    def __call__(self, database=None):
        if self._value:
            db = self.object_type._get_database(database)
            return self.object_type.get(self._value, database)
        else:
            return None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
