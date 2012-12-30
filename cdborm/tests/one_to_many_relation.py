from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.index import BaseIndex, Index
from cdborm.relation import OneToMany, OneToManyList
from cdborm.errors import CanNotOverwriteRelationVariable, AlreadyAssigned

class MyOtMModel_(Model):
    first = OneToManyList('MyOtMModel_1', 'MyOtMModel_1Foreign')

class MyOtMModel_1(Model):
    second = OneToMany('MyOtMModel_', 'MyOtMModel_1Foreign')

@Index('MyOtMModel_1')
class MyOtMModel_1Index(BaseIndex):
    clsName = 'MyOtMModel_1'

@Index('MyOtMModel_1Foreign')
class MyOtMModel_1ForeginIndex(BaseIndex):
    clsName = 'MyOtMModel_1'
    relation_key = 'second'

@Index('MyOtMModel_')
class MyOtMModel_Index(BaseIndex):
    clsName = 'MyOtMModel_'

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
        self.assertEqual(second.first(), [one,])

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
        self.assertEqual(second.first(), [one,one2])

    def test_assign_and_release(self):
        second = MyOtMModel_()
        second.save()

        one = MyOtMModel_1()
        one.second.assign(second)
        one.save()

        self.assertEqual(one.second(), second)
        self.assertEqual(second.first(), [one,])

        one.second.release()
        one.save()
        self.assertEqual(one.second(), None)
        self.assertEqual(second.first(), [])

    def test_new_objects(self):
        second = MyOtMModel_()
        self.assertEqual(second.first(), [])
        second.save()
        self.assertEqual(second.first(), [])

        one = MyOtMModel_1()
        self.assertEqual(one.second(), None)
        one.save()
        self.assertEqual(one.second(), None)
