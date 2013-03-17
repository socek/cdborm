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
        try:
            return self._value.toordinal()
        except AttributeError:
            return None

    def from_simple_value(self, value):
        try:
            self._value = self._class.fromordinal(value)
        except AttributeError:
            return None


class DateField(DateTimeField):
    _class = date
