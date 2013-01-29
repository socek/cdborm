from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.relation import ManyToMany
from cdborm.errors import CanNotOverwriteRelationVariable


class MyMtMModel_2(Model):
    first = ManyToMany('MyMtMModel_1')


class MyMtMModel_1(Model):
    second = ManyToMany('MyMtMModel_2')


class ManyToManyRelationTest(CdbOrmTestCase):

    def test_assign_fail(self):
        def bad_assign(one, second):
            one.second = second

        second = MyMtMModel_2()
        second.save()

        one = MyMtMModel_1()
        self.assertRaises(CanNotOverwriteRelationVariable, bad_assign, one, second)

    def test_assign_success(self):
        second = MyMtMModel_2()
        second.save()

        one = MyMtMModel_1()
        one.second.assign(second)
        one.save()

        self.assertEqual([second, ], one.second())
        self.assertEqual([one, ], second.first())

    def test_double_assign(self):
        second = MyMtMModel_2()
        second.save()

        one1 = MyMtMModel_1()
        one1.second.assign(second)
        one1.save()

        one2 = MyMtMModel_1()
        one2.second.assign(second)
        one2.save()

        self.assertEqual(one1.second(), [second, ])
        self.assertEqual(one2.second(), [second, ])
        self.assertEqual(second.first(), [one1, one2])

    def test_assign_and_release(self):
        second = MyMtMModel_2()
        second.save()

        one1 = MyMtMModel_1()
        one1.second.assign(second)
        one1.save()

        one2 = MyMtMModel_1()
        one2.second.assign(second)
        one2.save()

        self.assertEqual(one1.second(), [second, ])
        self.assertEqual(one2.second(), [second, ])
        self.assertEqual(second.first(), [one1, one2])

        one1.second.release(second)
        one1.save()
        self.assertEqual(one1.second(), [])
        self.assertEqual(one2.second(), [second, ])
        self.assertEqual(second.first(), [one2])

    def test_new_objects(self):
        second = MyMtMModel_2()
        self.assertEqual(second.first(), [])
        second.save()
        self.assertEqual(second.first(), [])

        one = MyMtMModel_1()
        self.assertEqual(one.second(), [])
        one.save()
        self.assertEqual(one.second(), [])

    def test_to_dict(self):
        second = MyMtMModel_2()
        second.save()

        one = MyMtMModel_1()
        one.second.assign(second)
        one.save()

        data = second._to_dict()
        self.assertEqual(data['_relation_first'], [one.id,])

        data = one._to_dict()
        self.assertEqual(data['_relation_second'], [second.id])

    def test_from_dict(self):
        obj2 = MyMtMModel_1()
        obj2.save()

        data = {
            '_relation_first' : obj2.id,
            '_type' : MyMtMModel_2.__name__,
            '_type_version' : 1,
        }
        obj1 = MyMtMModel_2.from_dict(data)
        obj1.save()

        self.assertEqual(obj1.first(), [obj2,])
        self.assertEqual(obj2.second(), [obj1,])

    def test_init(self):
        obj2 = MyMtMModel_1()
        obj2.save()

        obj1 = MyMtMModel_2(_relation_first=obj2.id)
        obj1.save()

        self.assertEqual(obj1.first(), [obj2,])
        self.assertEqual(obj2.second(), [obj1,])
