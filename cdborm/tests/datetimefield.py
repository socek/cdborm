from datetime import datetime

from dateutil import parser

from .base import CdbOrmTestCase
from cdborm.errors import BadValueType
from cdborm.fields import DateTimeField
from cdborm.model import Model


_default_value = datetime.now()
_default_value2 = datetime(2000, 10, 1, 1, 1, 1)


def make_default(value, parent):
    return _default_value


class MyDateTimeModel(Model):
    first = DateTimeField()
    second = DateTimeField()
    third = DateTimeField(default=make_default)
    fourth = DateTimeField(_default_value2)


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

        data = obj._to_dict(self.db)
        self.assertEqual(first.isoformat(), data['first'])

    def test_from_dict(self):
        data = {
            'first': datetime(2000, 10, 5).isoformat(),
            '_type': MyDateTimeModel.__name__,
            '_type_version': 1,
        }
        obj = MyDateTimeModel.from_dict(data)

        self.assertEqual(parser.parse(data['first']), obj.first)

    def test_init(self):
        data = {
            'first': datetime(2000, 10, 6),
        }
        obj = MyDateTimeModel(**data)

        self.assertEqual(data['first'], obj.first)

    def test_default(self):
        obj = MyDateTimeModel()
        self.assertEqual(_default_value, obj.third)
        self.assertEqual(_default_value2, obj.fourth)
