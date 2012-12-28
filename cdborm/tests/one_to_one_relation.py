from .base import CdbOrmTestCase
from cdborm.model import Model
from cdborm.index import BaseIndex, Index
from cdborm.relation import OneToOne
from cdborm.errors import CanNotOverwriteRelationVariable

class MyOtOModel_2(Model): pass

class MyOtOModel_1(Model):
    second = OneToOne(MyOtOModel_2)

@Index('MyOtOModel_1')
class MyOtOModel_1Index(BaseIndex):
    clsName = 'MyOtOModel_1'

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

