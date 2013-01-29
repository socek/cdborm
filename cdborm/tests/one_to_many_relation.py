from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.relation import OneToMany, OneToManyList
from cdborm.errors import CanNotOverwriteRelationVariable, BadType


class MyOtMModel_(Model):
    first = OneToManyList('MyOtMModel_1')


class MyOtMModel_1(Model):
    second = OneToMany('MyOtMModel_')


class OneToManyRelationTest(CdbOrmTestCase):

    def test_assign_fail(self):
        def bad_assign(one, second):
            one.second = second

        second = MyOtMModel_()
        second.save()

        one = MyOtMModel_1()
        self.assertRaises(CanNotOverwriteRelationVariable, bad_assign, one, second)

    def test_assign_success(self):
        second = MyOtMModel_()
        second.save()

        one = MyOtMModel_1()
        one.second.assign(second)
        one.save()

        self.assertEqual(one.second(), second)
        self.assertEqual(second.first(), [one, ])

    def test_double_assign(self):
        second = MyOtMModel_()
        second.save()

        one = MyOtMModel_1()
        one.second.assign(second)
        one.save()

        one2 = MyOtMModel_1()
        one2.second.assign(second)
        one2.save()

        self.assertEqual(one2.second(), second)
        self.assertEqual(second.first(), [one, one2])

    def test_assign_and_release(self):
        second = MyOtMModel_()
        second.save()

        one = MyOtMModel_1()
        one.second.assign(second)
        one.save()

        one_2 = MyOtMModel_1()
        one_2.second.assign(second)
        one_2.save()

        self.assertEqual(one.second(), second)
        self.assertEqual(one_2.second(), second)
        self.assertEqual(second.first(), [one, one_2])

        one.second.release()
        one.save()
        self.assertEqual(one.second(), None)
        self.assertEqual(one_2.second(), second)
        self.assertEqual(second.first(), [one_2])

    def test_assign_and_release_from_list(self):
        second = MyOtMModel_()
        second.save()

        one = MyOtMModel_1()
        one.second.assign(second)
        one.save()

        one_2 = MyOtMModel_1()
        one_2.second.assign(second)
        one_2.save()

        self.assertEqual(one.second(), second)
        self.assertEqual(one_2.second(), second)
        self.assertEqual(second.first(), [one, one_2])

        second.first.release(one)
        second.save()

        self.assertEqual(one.second(), None)
        self.assertEqual(one_2.second(), second)
        self.assertEqual(second.first(), [one_2])

    def test_new_objects(self):
        second = MyOtMModel_()
        self.assertEqual(second.first(), [])
        second.save()
        self.assertEqual(second.first(), [])

        one = MyOtMModel_1()
        self.assertEqual(one.second(), None)
        one.save()
        self.assertEqual(one.second(), None)

    def test_to_dict(self):
        second = MyOtMModel_()
        second.save()

        one = MyOtMModel_1()
        one.second.assign(second)
        one.save()

        data = second._to_dict()
        self.assertEqual(data['_relation_first'], [one.id,])

        data = one._to_dict()
        self.assertEqual(data['_relation_second'], second.id)

    def test_from_dict_1(self):
        obj2 = MyOtMModel_()
        obj2.save()

        data = {
            '_relation_second' : obj2.id,
            '_type' : MyOtMModel_1.__name__,
            '_type_version' : 1,
        }
        obj1 = MyOtMModel_1.from_dict(data)
        obj1.save()

        self.assertEqual(obj1.second(), obj2)
        self.assertEqual(obj2.first(), [obj1,])

    def test_from_dict_2(self):
        obj2 = MyOtMModel_1()
        obj2.save()

        data = {
            '_relation_first' : [obj2.id,],
            '_type' : MyOtMModel_.__name__,
            '_type_version' : 1,
        }
        obj1 = MyOtMModel_.from_dict(data)
        obj1.save()

        self.assertEqual(obj1.first(), [obj2,])
        self.assertEqual(obj2.second(), obj1)

    def test_init(self):
        obj2 = MyOtMModel_1()
        obj2.save()

        obj1 = MyOtMModel_(_relation_first=[obj2.id,])
        obj1.save()
        self.assertEqual(obj1.first(), [obj2,])
        self.assertEqual(obj2.second(), obj1)

    def test_bad_assign(self):
        obj1 = MyOtMModel_1()
        self.assertRaises(BadType, obj1.second.assign, obj1)
