from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.errors import BadType


class MyModel(Model):
    pass


class MySecondModel(Model):
    pass


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

    def test_get_without_cache(self):
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

    def test_all(self):
        self.assertEqual([], MyModel.all())

        obj = MyModel()
        obj.save()
        self.assertEqual([obj], MyModel.all())

        obj2 = MyModel()
        obj2.save()
        self.assertEqual([obj, obj2], MyModel.all())

        obj3 = MyModel()
        obj3.save()
        self.assertEqual([obj, obj2, obj3], MyModel.all())

    def test_all_without_cache(self):
        self.assertEqual([], MyModel.all())

        obj = MyModel()
        obj.save()
        obj2 = MyModel()
        obj2.save()
        obj3 = MyModel()
        obj3.save()

        Model.cache = {}

        data = [obj.id, obj2.id, obj3.id]
        all_elements = [obj.id for obj in MyModel.all()]
        self.assertEqual(data, all_elements)

    def test_remove(self):
        self.assertEqual([], MyModel.all())

        obj = MyModel()
        obj.save()

        self.assertEqual([obj], MyModel.all())

        obj.delete()
        self.assertEqual([], MyModel.all())

    def test_clear_cache(self):
        obj1 = MyModel()
        obj1.save()

        obj2 = MyModel.get(obj1.id)

        MyModel.clear_cache()

        obj3 = MyModel.get(obj1.id)
        obj3.save()

        self.assertEqual(id(obj1), id(obj2))
        self.assertNotEqual(id(obj1), id(obj3))

