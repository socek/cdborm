from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.index import BaseIndex, Index, LinkIndex
from cdborm.relation import ManyToMany
from cdborm.errors import CanNotOverwriteRelationVariable, AlreadyAssigned


class MyMtMModel_2(Model):
    first = ManyToMany('MyMtMModel_1', 'MyMtMModel_1.to.MyMtMModel_2')


class MyMtMModel_1(Model):
    second = ManyToMany('MyMtMModel_2', 'MyMtMModel_2.to.MyMtMModel_1')


@Index('MyMtMModel_1')
class MyMtMModel_1Index(BaseIndex):
    clsName = 'MyMtMModel_1'


@Index('MyMtMModel_2')
class MyMtMModel_Index(BaseIndex):
    clsName = 'MyMtMModel_2'


@Index('MyMtMModel_1.to.MyMtMModel_2')
class MyMtMModel_1ForeginIndex(LinkIndex):
    key = 'MyMtMModel_2'


@Index('MyMtMModel_2.to.MyMtMModel_1')
class MyMtMModel_2ForeginIndex(LinkIndex):
    key = 'MyMtMModel_1'


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
