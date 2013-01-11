from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.relation import OneToOne
from cdborm.errors import CanNotOverwriteRelationVariable


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

    def test_new_objects(self):
        second = MyOtOModel_2()
        self.assertEqual(second.first(), None)
        second.save()
        self.assertEqual(second.first(), None)

        one = MyOtOModel_1()
        self.assertEqual(one.second(), None)
        one.save()
        self.assertEqual(one.second(), None)
