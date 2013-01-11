from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.fields import IntField
from cdborm.errors import FieldValidationError


class MyIntModel(Model):
    first = IntField()
    second = IntField(nullable=False)


class IntFieldTest(CdbOrmTestCase):

    def test_simple_assigning(self):
        value = 10
        obj = MyIntModel()
        obj.first = value

        self.assertEqual(value, obj.first)

    def test_string_assiging_success(self):
        obj = MyIntModel()
        obj.first = '11'

        self.assertEqual(11, obj.first)

    def test_string_assiging_fail(self):
        def bad_assign():
            obj.first = 'aa'

        obj = MyIntModel()
        self.assertRaises(ValueError, bad_assign)

    def test_save_and_restore(self):
        value = 10
        obj = MyIntModel()
        obj.second = value
        obj.save()

        Model.cache = {}

        obj2 = MyIntModel.get(obj.id)

        self.assertEqual(value, obj2.second)
        self.assertEqual(None, obj2.first)

    def test_field_validation_error(self):
        obj = MyIntModel()
        try:
            obj.save()
        except FieldValidationError, er:
            self.assertEqual(er.model_name, obj._get_full_class_name())
            self.assertEqual(er.field_name, 'second')
