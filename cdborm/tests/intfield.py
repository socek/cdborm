from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.fields import IntField
from cdborm.errors import FieldValidationError

_default_value = 1
_default_value2 = 2
_default_value3 = 3

def make_default(value, parent):
    return _default_value

def make_default_no_args():
    return _default_value3

def make_bad_default(one):
    return 4

class MyIntModel(Model):
    first = IntField()
    second = IntField(nullable=False)
    third = IntField(default=make_default)
    fourth = IntField(_default_value2)
    five = IntField(default=make_default_no_args)

    @property
    def name(self):
        return self.first

class MyIntModelBadDefault(Model):
    bad = IntField(default=make_bad_default)


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
            self.assertEqual(type(repr(er)), str)
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

        data = obj._to_dict(self.db)
        self.assertEqual(first, data['first'])
        self.assertEqual(second, data['second'])

    def test_from_dict(self):
        data = {
            'first': 45,
            'second': 55,
            '_type': MyIntModel.__name__,
            '_type_version': 1,
        }
        obj = MyIntModel.from_dict(data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)

    def test_init(self):
        data = {
            'first': 45,
            'second': 55,
        }
        obj = MyIntModel(**data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)

    def test_default(self):
        obj = MyIntModel()
        self.assertEqual(_default_value, obj.third)
        self.assertEqual(_default_value2, obj.fourth)
        self.assertEqual(_default_value3, obj.five)

    def test_bad_default(self):
        self.assertRaises(TypeError, MyIntModelBadDefault)
