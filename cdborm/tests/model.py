from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.index import BaseIndex, Index
from cdborm.errors import BadType

class MyModel(Model): pass

class MySecondModel(Model): pass

@Index('MyModel')
class MyModelIndex(BaseIndex):
    clsName = 'MyModel'

@Index('MySecondModel')
class MyModelIndex(BaseIndex):
    clsName = 'MySecondModel'


class ModelTest(CdbOrmTestCase):

    def test_save(self):
        obj = MyModel()
        obj.save()
        self.assertEqual(type(obj.id), str)

    def test_get_with_cache(self):
        obj = MyModel()
        obj.save()

        second_obj = MyModel.get(obj.id)
        self.assertEqual(second_obj.id, obj.id)
        self.assertEqual(id(second_obj), id(obj))

    def test_without_cache(self):
        obj = MyModel()
        obj.save()

        Model.cache = {}
        second_obj = MyModel.get(obj.id)
        self.assertEqual(second_obj.id, obj.id)
        self.assertNotEqual(id(second_obj), id(obj))

    def test_wrong_type(self):
        obj = MyModel()
        obj.save()

        obj2 = MySecondModel()
        obj2.save()

        self.assertRaises(BadType, MyModel.get, (obj2.id))
