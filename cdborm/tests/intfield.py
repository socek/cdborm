from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.fields import IntField
from cdborm.errors import FieldValidationError

class MyIntModel(Model):
    first = IntField()
    second = IntField(nullable=False)

    @property
    def name(self):
        return self.first

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

    def test_initial_data(self):
        first = 20
        second = 25
        obj = MyIntModel(
            first=first,
            second=second,
        )
        self.assertEqual(first, obj.first)
        self.assertEqual(second, obj.second)
        self.assertEqual(obj.name, first)

        obj.save()

        self.assertEqual(first, obj.first)
        self.assertEqual(second, obj.second)
        self.assertEqual(obj.name, first)

    def test_to_dict(self):
        first = 30
        second = 35
        obj = MyIntModel(
            first=first,
            second=second,
        )

        obj.save()

        data = obj._to_dict()
        self.assertEqual(first, data['first'])
        self.assertEqual(second, data['second'])

    def test_from_dict(self):
        data = {
            'first' : 45,
            'second' : 55,
            '_type' : MyIntModel.__name__,
            '_type_version' : 1,
        }
        obj = MyIntModel.from_dict(data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)

    def test_init(self):
        data = {
            'first' : 45,
            'second' : 55,
        }
        obj = MyIntModel(**data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)
