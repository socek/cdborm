from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.index import BaseIndex, Index
from cdborm.relation import OneToOne, OneToOneForeign
from cdborm.errors import CanNotOverwriteRelationVariable, AlreadyAssigned

class MyOtOModel_2(Model):
    first = OneToOneForeign('MyOtOModel_1', 'MyOtOModel_1Foreign')

class MyOtOModel_1(Model):
    second = OneToOne('MyOtOModel_2', 'MyOtOModel_1Foreign')

@Index('MyOtOModel_1')
class MyOtOModel_1Index(BaseIndex):
    clsName = 'MyOtOModel_1'

@Index('MyOtOModel_1Foreign')
class MyOtOModel_1ForeginIndex(BaseIndex):
    clsName = 'MyOtOModel_1'
    key = '_relation_second'

@Index('MyOtOModel_2')
class MyOtOModel_2Index(BaseIndex):
    clsName = 'MyOtOModel_2'

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

    def test_assign_double_assign_fail(self):
        second = MyOtOModel_2()
        second.save()

        one = MyOtOModel_1()
        one.second.assign(second)
        one.save()

        one2 = MyOtOModel_1()
        self.assertRaises(AlreadyAssigned, one2.second.assign, second)

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
