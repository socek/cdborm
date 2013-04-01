from .field import Field


class ListField(Field):

    def _setter(self, value):
        if type(value) in [list, tuple]:
            self._value = value
        else:
            raise ValueError(u'Value must be a list or tuple!')
