from cdborm.errors import FieldCanNotBeNull
class Field(object):
    _value = None

    def __init__(self, value=None, nullable=True):
        self._nullable = nullable
        if value:
            self.value = value

    @property
    def value(self):
        return self._getter()

    def _getter(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._nullable and value == None:
            self._value = None
        else:
            if value == None:
                raise FieldCanNotBeNull()
            else:
                self._setter(value)

    def _setter(self, value):
        self._value = value

    def validate(self):
        if self._nullable == False and self._value == None:
            return (False, 'This field can not be null!')
        return (True, None)

class StringField(Field):

    def _setter(self, value):
        if type(value) == unicode:
            return text
        elif type(text) == str:
            return text.decode('utf8')
        else:
            raise ValueError(u'Value must be a string or unicode!')

class IntField(Field):
    def _setter(self, value):
        self._value = int(value)

class IdField(Field): pass
class RevField(Field): pass
class TypeVersionField(IntField): pass
class TypeField(Field): pass
