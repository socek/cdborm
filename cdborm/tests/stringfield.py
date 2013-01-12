from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.fields import StringField
from cdborm.errors import FieldValidationError

_test_name = 'something'


class MyStringModel(Model):
    first = StringField()
    second = StringField(nullable=False)

    @property
    def name(self):
        return _test_name


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

    def test_initial_data(self):
        first = 'something 1'
        second = 'something 2'
        obj = MyStringModel(
            first=first,
            second=second,
        )
        self.assertEqual(first, obj.first)
        self.assertEqual(second, obj.second)
        self.assertEqual(obj.name, _test_name)

        obj.save()

        self.assertEqual(first, obj.first)
        self.assertEqual(second, obj.second)
        self.assertEqual(obj.name, _test_name)
