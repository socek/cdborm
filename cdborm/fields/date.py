from datetime import datetime, date
from cdborm.errors import BadValueType
from .field import Field


class DateTimeField(Field):

    _class = datetime

    def _setter(self, value):
        if type(value) == self._class:
            self._value = value
        else:
            raise BadValueType()

    def to_simple_value(self):
        return self._value.toordinal()

    def from_simple_value(self, value):
        self._value = self._class.fromordinal(value)


class DateField(DateTimeField):
    _class = date
