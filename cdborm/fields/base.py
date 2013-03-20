from .field import Field
from .int import IntField
from .string import StringField


class IdField(Field):
    pass


class TypeVersionField(IntField):

    def _setter(self, value):
        value = value._type_version
        super(TypeVersionField, self)._setter(value)


class TypeField(StringField):

    def _setter(self, value):
        value = value._get_full_class_name()
        super(TypeField, self)._setter(value)
