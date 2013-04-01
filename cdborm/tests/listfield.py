from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.fields import ListField
from cdborm.errors import FieldValidationError

_default_value = [1,2,]
_default_value2 = (2,3,)

def make_default(value, parent):
    return _default_value


class MyListModel(Model):
    first = ListField()
    second = ListField(nullable=False)
    third = ListField(default=make_default)
    fourth = ListField(_default_value2)

    @property
    def name(self):
        return self.first


class ListFieldTest(CdbOrmTestCase):

    def test_simple_assigning(self):
        value = [3,4]
        obj = MyListModel()
        obj.first = value

        self.assertEqual(value, obj.first)

    def test_string_assiging_fail(self):
        def bad_assign():
            obj.first = 'aa'

        obj = MyListModel()
        self.assertRaises(ValueError, bad_assign)

    def test_save_and_restore(self):
        value = [4,5]
        obj = MyListModel()
        obj.second = value
        obj.save()

        Model.cache = {}

        obj2 = MyListModel.get(obj.id)

        self.assertEqual(value, obj2.second)
        self.assertEqual(None, obj2.first)

    def test_field_validation_error(self):
        obj = MyListModel()
        try:
            obj.save()
        except FieldValidationError, er:
            self.assertEqual(type(repr(er)), str)
            self.assertEqual(er.model_name, obj._get_full_class_name())
            self.assertEqual(er.field_name, 'second')

    def test_initial_data(self):
        first = [5,6]
        second = [6,7]
        obj = MyListModel(
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
        first = [7,8]
        second = [8,9]
        obj = MyListModel(
            first=first,
            second=second,
        )

        obj.save()

        data = obj._to_dict(self.db)
        self.assertEqual(first, data['first'])
        self.assertEqual(second, data['second'])

    def test_from_dict(self):
        data = {
            'first': [9,10],
            'second': [10,11],
            '_type': MyListModel.__name__,
            '_type_version': 1,
        }
        obj = MyListModel.from_dict(data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)

    def test_init(self):
        data = {
            'first': [11,12],
            'second': [12,13],
        }
        obj = MyListModel(**data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)

    def test_default(self):
        obj = MyListModel()
        self.assertEqual(_default_value, obj.third)
        self.assertEqual(_default_value2, obj.fourth)
