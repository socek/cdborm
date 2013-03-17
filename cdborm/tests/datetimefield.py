from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.fields import DateTimeField
from cdborm.errors import BadValueType
from datetime import datetime

class MyDateTimeModel(Model):
    first = DateTimeField()

class DateTimeFieldTest(CdbOrmTestCase):

    def test_simple_assigning(self):
        value = datetime(2000, 10, 1)
        obj = MyDateTimeModel()
        obj.first = value

        self.assertEqual(value, obj.first)

    def test_string_assiging_fail(self):
        def bad_assign():
            obj.first = 'aa'

        obj = MyDateTimeModel()
        self.assertRaises(BadValueType, bad_assign)

    def test_save_and_restore(self):
        value = datetime(2000, 10, 2)
        obj = MyDateTimeModel()
        obj.first = value
        obj.save()

        Model.cache = {}

        obj2 = MyDateTimeModel.get(obj.id)

        self.assertEqual(value, obj2.first)

    def test_initial_data(self):
        first = datetime(2000, 10, 3)
        obj = MyDateTimeModel(
            first=first,
        )
        self.assertEqual(first, obj.first)

        obj.save()

        self.assertEqual(first, obj.first)

    def test_to_dict(self):
        first = datetime(2000, 10, 4)
        obj = MyDateTimeModel(
            first=first,
        )

        obj.save()

        data = obj._to_dict()
        self.assertEqual(first.toordinal(), data['first'])

    def test_from_dict(self):
        data = {
            'first' : datetime(2000, 10, 5).toordinal(),
            '_type' : MyDateTimeModel.__name__,
            '_type_version' : 1,
        }
        obj = MyDateTimeModel.from_dict(data)

        self.assertEqual(datetime.fromordinal(data['first']), obj.first)

    def test_init(self):
        data = {
            'first' : datetime(2000, 10, 6),
        }
        obj = MyDateTimeModel(**data)

        self.assertEqual(data['first'], obj.first)
