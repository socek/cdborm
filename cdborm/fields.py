class BaseField(object):
    _value = None

    @property
    def value(self):
        return self._getter()

    def _getter(self):
        return self._value

    @value.setter
    def value(self, value):
        self._setter(value)

    def _setter(self, value):
        self._value = value

class NormalField(BaseField): pass

class IntField(BaseField):
    def _setter(self, value):
        self._value = int(value)
