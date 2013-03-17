from .field import Field


class StringField(Field):

    def _setter(self, value):
        if type(value) == unicode:
            self._value = value
        elif type(value) == str:
            self._value = value.decode('utf8')
        else:
            raise ValueError(u'Value must be a string or unicode!')
