from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.relation import OneToOne
from cdborm.errors import CanNotOverwriteRelationVariable, BadType


class MyOtOModel_2(Model):
    first = OneToOne('MyOtOModel_1')


class MyOtOModel_1(Model):
    second = OneToOne('MyOtOModel_2')


class OneToOneRelationTest(CdbOrmTestCase):

    def test_assign_fail(self):
        def bad_assign(one, second):
            one.second = second

        second = MyOtOModel_2()
        second.save()

        one = MyOtOModel_1()
        self.assertRaises(CanNotOverwriteRelationVariable, bad_assign, one, second)

    def test_assign_success(self):
        second = MyOtOModel_2()
        second.save()

        one = MyOtOModel_1()
        one.second.assign(second)
        one.save()

        self.assertEqual(one.second(), second)
        self.assertEqual(second.first(), one)

    def test_double_assign(self):
        second = MyOtOModel_2()
        second.save()

        one = MyOtOModel_1()
        one.second.assign(second)
        one.save()

        one2 = MyOtOModel_1()
        one2.second.assign(second)
        one2.save()

        self.assertEqual(one.second(), None)
        self.assertEqual(one2.second(), second)
        self.assertEqual(second.first(), one2)

    def test_assign_and_release(self):
        second = MyOtOModel_2()
        second.save()

        one = MyOtOModel_1()
        one.second.assign(second)
        one.save()

        self.assertEqual(one.second(), second)
        self.assertEqual(second.first(), one)

        one.second.release()
        one.save()
        self.assertEqual(one.second(), None)
        self.assertEqual(second.first(), None)

    def test_assign_and_release2(self):
        one = MyOtOModel_1()
        one.save()

        second = MyOtOModel_2()
        second.first.assign(one)
        second.save()

        self.assertEqual(one.second(), second)
        self.assertEqual(second.first(), one)

        second.first.release()
        second.save()
        self.assertEqual(one.second(), None)
        self.assertEqual(second.first(), None)

    def test_new_objects(self):
        second = MyOtOModel_2()
        self.assertEqual(second.first(), None)
        second.save()
        self.assertEqual(second.first(), None)

        one = MyOtOModel_1()
        self.assertEqual(one.second(), None)
        one.save()
        self.assertEqual(one.second(), None)

    def test_to_dict(self):
        second = MyOtOModel_2()
        second.save()

        one = MyOtOModel_1()
        one.second.assign(second)
        one.save()

        data = second._to_dict()
        self.assertEqual(data['_relation_first'], one.id)

        data = one._to_dict()
        self.assertEqual(data['_relation_second'], second.id)

    def test_from_dict(self):
        obj2 = MyOtOModel_2()
        obj2.save()

        data = {
            '_relation_second' : obj2.id,
            '_type' : MyOtOModel_1.__name__,
            '_type_version' : 1,
        }
        obj1 = MyOtOModel_1.from_dict(data)
        obj1.save()

        self.assertEqual(obj1.second(), obj2)
        self.assertEqual(obj2.first(), obj1)

    def test_init(self):
        obj2 = MyOtOModel_2()
        obj2.save()

        data = {
            'second' : obj2,
        }
        obj1 = MyOtOModel_1(**data)
        obj1.save()

        self.assertEqual(obj1.second(), obj2)
        self.assertEqual(obj2.first(), obj1)

    def test_bad_assign(self):
        obj1 = MyOtOModel_2()
        self.assertRaises(BadType, obj1.first.assign, obj1)
