from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.relation import OneToMany, OneToManyList


class MyOtMModel_3(Model):
    first_all = OneToManyList('MyOtMModel_4', 'first')
    second_all = OneToManyList('MyOtMModel_4', 'second')


class MyOtMModel_4(Model):
    first = OneToMany('MyOtMModel_3', 'first')
    second = OneToMany('MyOtMModel_3', 'second')


class OneToManySubnameRelationTest(CdbOrmTestCase):

    def test_assigning(self):
        mall = MyOtMModel_3()
        mall.save()

        first = MyOtMModel_4()
        first.first.assign(mall)
        first.save()

        second = MyOtMModel_4()
        second.second.assign(mall)
        second.save()

        self.assertEqual(mall.first_all(), [first])
        self.assertEqual(mall.second_all(), [second])
        self.assertEqual(first.first(), mall)
        self.assertEqual(second.second(), mall)
