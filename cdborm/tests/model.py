from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.errors import BadType, FieldCanNotBeNull
from cdborm.fields import StringField, IntField, Field
from cdborm.relation import OneToMany, OneToManyList


class MyModel(Model):
    name1 = StringField()
    year1 = IntField()
    rel1 = OneToMany('MySecondModel')


class MySecondModel(Model):
    name2 = StringField()
    year2 = IntField()
    rel2 = OneToManyList('MyModel')


class MyThirdModel(Model):
    field = Field(nullable=False)
    nullfield = Field()


class ModelTest(CdbOrmTestCase):

    def test_save(self):
        obj = MyModel()
        obj.save()
        self.assertEqual(type(obj.id), str)

        data = obj._to_dict(self.db)
        for key in ['_type', '_type_version', '_rev', '_relation_rel1', '_id']:
            self.assertTrue(key in data)

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

    def test_to_dict(self):
        obj1 = MyModel()
        data = obj1._to_dict(self.db)

        self.assertEqual(MyModel.__name__, data['_type'])
        self.assertEqual(1, data['_type_version'])
        self.assertEqual(None, data['_relation_rel1'])

    def test_to_dict_without_db(self):
        obj1 = MyModel()
        data = obj1._to_dict(None)

        self.assertEqual(MyModel.__name__, data['_type'])
        self.assertEqual(1, data['_type_version'])
        self.assertTrue(not '_relation_rel1' in data)

    def test_cannotbenull(self):
        def bad_assign():
            obj1.field = None
        #-----------------------------------------------------------------------
        obj1 = MyThirdModel()
        self.assertRaises(FieldCanNotBeNull, bad_assign)

    def test_canbenull(self):
        obj1 = MyThirdModel()
        obj1.nullfield = None

        self.assertEqual(None, obj1.nullfield)

    def test_id(self):
        obj1 = MyModel()
        self.assertEqual(None, obj1.id)

    def test_fromdict_bad(self):
        self.assertRaises(BadType, MyModel.from_dict, {'_type': 'bad type'})
