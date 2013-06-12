from .field import Field


class FloatField(Field):

    def _setter(self, value):
        self._value = float(value)
