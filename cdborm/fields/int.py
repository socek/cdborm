from .field import Field


class IntField(Field):

    def _setter(self, value):
        self._value = int(value)
