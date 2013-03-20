from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.fields import StringField
from cdborm.errors import FieldValidationError


class MyStringModel(Model):
    first = StringField()
    second = StringField(nullable=False)

    @property
    def name(self):
        return self.first


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

    def test_bad_assign(self):
        def bad_assign(obj):
            obj.first = 123
        #-----------------------------------------------------------------------
        obj = MyStringModel()
        self.assertRaises(ValueError, bad_assign, obj)

    def test_initial_data(self):
        first = 'something 1'
        second = 'something 2'
        obj = MyStringModel(
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
        first = 'something 1'
        second = 'something 2'
        obj = MyStringModel(
            first=first,
            second=second,
        )

        obj.save()

        data = obj._to_dict(self.db)
        self.assertEqual(first, data['first'])
        self.assertEqual(second, data['second'])

    def test_from_dict(self):
        data = {
            'first': '1 something 1',
            'second': '1 something 2',
            '_type': MyStringModel.__name__,
            '_type_version': 1,
        }
        obj = MyStringModel.from_dict(data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)

    def test_init(self):
        data = {
            'first': '1 something 1',
            'second': '1 something 2',
        }
        obj = MyStringModel(**data)

        self.assertEqual(data['first'], obj.first)
        self.assertEqual(data['second'], obj.second)
