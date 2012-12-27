from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.index import BaseIndex, Index
from cdborm.fields import StringField
from cdborm.errors import FieldValidationError

class MyStringModel(Model):
    first = StringField()
    second = StringField(nullable=False)

@Index('MyStringModel')
class MyStringModelIndex(BaseIndex):
    clsName = 'MyStringModel'


class StringFieldTest(CdbOrmTestCase):

    def test_simple_assigning(self):
        value = u'string test'
        obj = MyStringModel()
        obj.first = value

        self.assertEqual(value, obj.first)

    def test_string_assiging_success(self):
        obj = MyStringModel()
        obj.first = 'str to unicode'

        self.assertEqual(u'str to unicode', obj.first)

    def test_save_and_restore(self):
        value = u'good'
        obj = MyStringModel()
        obj.second = value
        obj.save()

        Model.cache = {}

        obj2 = MyStringModel.get(obj.id)

        self.assertEqual(value, obj2.second)
        self.assertEqual(None, obj2.first)

    def test_field_validation_error(self):
        obj = MyStringModel()
        try:
            obj.save()
        except FieldValidationError, er:
            self.assertEqual(er.model_name, obj._get_full_class_name())
            self.assertEqual(er.field_name, 'second')
