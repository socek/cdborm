from .base import CdbOrmMultiDbTestCase

from cdborm.model import Model
from cdborm import relation
from cdborm import fields

class MultiDatabaseTest(CdbOrmMultiDbTestCase):

    def test_simple_values(self):
        class ModelA(Model):
            string = fields.StringField()
            integer = fields.IntField()

        obj = ModelA()
        obj.string = 'str'
        obj.integer = 10
        obj.save(self.db)

        ModelA.clear_cache()

        obj_a = ModelA.get(obj.id, self.db)
        obj_a.save(self.db2)
        newid = obj_a.id

        ModelA.clear_cache()

        obj_b = ModelA.get(newid, self.db2)

        for test_obj in [obj_a, obj_b]:
            for key in ['id', 'string', 'integer']:
                self.assertEqual(getattr(obj, key), getattr(test_obj, key))
            self.assertNotEqual(obj['_rev'], test_obj['_rev'])

    def test_one_to_one_relation(self):
        class ModelA(Model):
            one = relation.OneToOne('ModelB')
            two = relation.OneToOne('ModelB', 'name2')
            data = fields.IntField()

        class ModelB(Model):
            one = relation.OneToOne('ModelA')
            two = relation.OneToOne('ModelA', 'name2')
            data = fields.IntField()

        def init_objects():
            obja1 = ModelA()
            obja1.data = 1
            obja1.save(self.db)

            obja2 = ModelA()
            obja2.data = 2
            obja2.save(self.db)

            objb = ModelB()
            objb.one.assign(obja1)
            objb.two.assign(obja2)
            objb.data = 3
            objb.save(self.db)

            return obja1, obja2, objb

        obja1, obja2, objb = init_objects()

        objb._update_relation_cache(self.db)

        ModelA.clear_cache()

        # obj_a1_d1 = ModelA.get(obja1.id, self.db)
        # obj_a2_d1 = ModelA.get(obja2.id, self.db)

        # obj_b_d1 = ModelB.get(objb.id, self.db)
        # obj_b_d1.save(self.db2)
        # newid = obj_b_d1.id

        # ModelA.clear_cache()

        # obj_b_d2 = ModelB.get(newid, self.db2)
        # self.assertEqual(None, obj_b_d2.one(self.db2))
        # self.assertEqual(None, obj_b_d2.two(self.db2))

        # obj_a1_d1.save(self.db2)

        # obj_a1_d2 = obj_b_d2.one(self.db2)

        # self.assertNotEqual(None, obj_b_d2.one(self.db2))
        # self.assertEqual(obj_a1_d2.data, obj_b_d2.one(self.db2).data)
        # self.assertEqual(None, obj_b_d2.two(self.db2))

        # obj_a2_d1.save(self.db2)

        # obj_a2_d2 = obj_b_d2.two(self.db2)

        # self.assertNotEqual(None, obj_b_d2.two(self.db2))
        # self.assertEqual(obj_a1_d2.data, obj_b_d2.one(self.db2).data)
        # self.assertEqual(obj_a2_d2.data, obj_b_d2.two(self.db2).data)
