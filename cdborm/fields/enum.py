from .field import Field


class EnumField(Field):

    def __init__(self, enum_list, value=None, nullable=True, default=None):
        self.enum_list = enum_list
        super(EnumField, self).__init__(value, nullable, default)

    def _setter(self, value):
        if value in self.enum_list:
            self._value = value
        else:
            raise ValueError(u'Value not in enum list.')
