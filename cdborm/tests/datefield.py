from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.fields import DateField
from cdborm.errors import BadValueType
from datetime import date

class MyDateModel(Model):
    first = DateField()

class DateFieldTest(CdbOrmTestCase):

    def test_simple_assigning(self):
        value = date(2000, 10, 1)
        obj = MyDateModel()
        obj.first = value

        self.assertEqual(value, obj.first)

    def test_string_assiging_fail(self):
        def bad_assign():
            obj.first = 'aa'

        obj = MyDateModel()
        self.assertRaises(BadValueType, bad_assign)

    def test_save_and_restore(self):
        value = date(2000, 10, 2)
        obj = MyDateModel()
        obj.first = value
        obj.save()

        Model.cache = {}

        obj2 = MyDateModel.get(obj.id)

        self.assertEqual(value, obj2.first)

    def test_initial_data(self):
        first = date(2000, 10, 3)
        obj = MyDateModel(
            first=first,
        )
        self.assertEqual(first, obj.first)

        obj.save()

        self.assertEqual(first, obj.first)

    def test_to_dict(self):
        first = date(2000, 10, 4)
        obj = MyDateModel(
            first=first,
        )

        obj.save()

        data = obj._to_dict(self.db)
        self.assertEqual(first.toordinal(), data['first'])

    def test_from_dict(self):
        data = {
            'first' : date(2000, 10, 5).toordinal(),
            '_type' : MyDateModel.__name__,
            '_type_version' : 1,
        }
        obj = MyDateModel.from_dict(data)

        self.assertEqual(date.fromordinal(data['first']), obj.first)

    def test_init(self):
        data = {
            'first' : date(2000, 10, 6),
        }
        obj = MyDateModel(**data)

        self.assertEqual(data['first'], obj.first)
