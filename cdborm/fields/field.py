from cdborm.errors import FieldCanNotBeNull
from copy import copy


class Field(object):
    _value = None

    def __init__(self, value=None, nullable=True, default=None):
        self._nullable = nullable
        if value:
            self.value = copy(value)
        self.default = default

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

    def to_simple_value(self):
        return self._value

    def from_simple_value(self, value):
        self._value = value

    def make_default(self, parent):
        if self.value is None and self.default:
            try:
                self.value = self.default(self, parent)
            except TypeError:
                self.value = self.default()
