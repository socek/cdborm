from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.fields import EnumField
from cdborm.errors import FieldValidationError

_default_value = 'second'
_default_value2 = 'first'


def make_default(value, parent):
    return _default_value

enum_list = ['first', 'second']


class MyStringModel1(Model):
    first = EnumField(enum_list)
    second = EnumField(enum_list)

    @property
    def name(self):
        return self.first


class MyStringModel2(Model):
    second = EnumField(enum_list, nullable=False)


class MyStringModel3(Model):
    third = EnumField(enum_list, default=make_default)
    fourth = EnumField(enum_list, _default_value2)


class EnumFieldTest(CdbOrmTestCase):

    def test_simple_assigning(self):
        value = enum_list[0]
        obj = MyStringModel1()
        obj.first = value

        self.assertEqual(value, obj.first)

    def test_string_assiging_fail(self):
        obj = MyStringModel1()
        def fun():
            obj.first ='str'

        self.assertRaises(ValueError, fun)

    def test_save_and_restore(self):
        value = enum_list[0]
        obj = MyStringModel1()
        obj.second = value
        obj.save()

        Model.cache = {}

        obj2 = MyStringModel1.get(obj.id)

        self.assertEqual(value, obj2.second)
        self.assertEqual(None, obj2.first)

    def test_field_validation_error(self):
        obj = MyStringModel2()
        try:
            obj.save()
        except FieldValidationError, er:
            self.assertEqual(er.model_name, obj._get_full_class_name())
            self.assertEqual(er.field_name, 'second')

    def test_bad_assign(self):
        def bad_assign(obj):
            obj.first = 123
        #----------------------------------------------------------------------
        obj = MyStringModel1()
        self.assertRaises(ValueError, bad_assign, obj)

    def test_initial_data(self):
        first = enum_list[0]
        second = enum_list[1]
        obj = MyStringModel1(
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
        first = 'first'
        second = 'second'
        obj = MyStringModel1(
            first=first,
            second=second,
        )

        obj.save()

        data = obj._to_dict(self.db)
        self.assertEqual(first, data['first'])
        self.assertEqual(second, data['second'])

    def test_from_dict(self):
        data = {
            'first': 'first',
            'second': 'second',
            '_type': MyStringModel1.__name__,
            '_type_version': 1,
        }
        obj = MyStringModel1.from_dict(data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)

    def test_init(self):
        data = {
            'first': 'first',
            'second': 'second',
        }
        obj = MyStringModel1(**data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)

    def test_default(self):
        obj = MyStringModel3()
        self.assertEqual(_default_value, obj.third)
        self.assertEqual(_default_value2, obj.fourth)
