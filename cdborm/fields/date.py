from datetime import datetime, date
from cdborm.errors import BadValueType
from .field import Field
import dateutil.parser


class DateTimeField(Field):

    _class = datetime

    def _setter(self, value):
        if type(value) == self._class:
            self._value = value
        else:
            raise BadValueType()

    def to_simple_value(self):
        return self._value.isoformat()

    def from_simple_value(self, value):
        self._value = dateutil.parser.parse(value)


class DateField(DateTimeField):
    _class = date

    def from_simple_value(self, value):
        super(DateField, self).from_simple_value(value)
        self._value = self._value.date()
