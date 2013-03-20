from .base import CdbOrmMultiDbTestCase

from cdborm.model import Model
from cdborm import relation
from cdborm import fields


class ModelAm2m(Model):
    one = relation.ManyToMany('ModelBm2m')
    two = relation.ManyToMany('ModelBm2m', 'name2')
    data = fields.IntField()


class ModelBm2m(Model):
    one = relation.ManyToMany('ModelAm2m')
    two = relation.ManyToMany('ModelAm2m', 'name2')
    data = fields.IntField()


class MultiDatabaseM2MTest(CdbOrmMultiDbTestCase):
    def setUp(self):
        def init_objects():
            data = {}

            data['a1'] = ModelAm2m()
            data['a1'].data = 1
            data['a1'].save(self.db)

            data['a2'] = ModelAm2m()
            data['a2'].data = 2
            data['a2'].save(self.db)

            data['b'] = ModelBm2m()
            data['b'].one.assign(data['a1'])
            data['b'].two.assign(data['a2'])
            data['b'].data = 10
            data['b'].save(self.db)

            return data

        super(MultiDatabaseM2MTest, self).setUp()
        self.initdata = init_objects()
        ModelAm2m.clear_cache()

        self.db1data = self.get_elements_from_db(self.db)
        ModelAm2m.clear_cache()

        self.db2data = {}

    def get_elements_from_db(self, db):
        return {
            'a1': ModelAm2m.get(self.initdata['a1'].id, db),
            'a2': ModelAm2m.get(self.initdata['a2'].id, db),
            'b': ModelBm2m.get(self.initdata['b'].id, db),
        }

    def test_copy_main_object(self):
        self.db1data['b'].copy_to_db(self.db2)
        ModelAm2m.clear_cache()
        self.db2data['b'] = ModelBm2m.get(self.initdata['b'].id, self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual([], self.db2data['b'].one(self.db2))
        self.assertEqual([], self.db2data['b'].two(self.db2))

    def test_copy_main_object_with_relation(self):
        self.db1data['b'].copy_to_db(self.db2, self.db)
        ModelAm2m.clear_cache()
        self.db2data['b'] = ModelBm2m.get(self.initdata['b'].id, self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual([], self.db2data['b'].one(self.db2))
        self.assertEqual([], self.db2data['b'].two(self.db2))

    def test_copy_subobject_object_with_relation(self):
        self.db1data['b'].copy_to_db(self.db2, self.db)
        self.db1data['a1'].copy_to_db(self.db2, self.db)
        self.db1data['a2'].copy_to_db(self.db2, self.db)
        ModelAm2m.clear_cache()
        self.db2data = self.get_elements_from_db(self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertEqual(self.db1data['a2'].data, self.db2data['b'].two(self.db2)[0].data)
        self.assertEqual(1, len(self.db2data['b'].one(self.db2)))
        self.assertEqual(1, len(self.db2data['b'].two(self.db2)))
        self.assertEqual(1, len(self.db2data['a1'].one(self.db2)))
        self.assertEqual(0, len(self.db2data['a1'].two(self.db2)))
        self.assertEqual(0, len(self.db2data['a2'].one(self.db2)))
        self.assertEqual(1, len(self.db2data['a2'].two(self.db2)))
        self.assertEqual(self.db1data['b'].data, self.db2data['a1'].one(self.db2)[0].data)
        self.assertEqual(self.db1data['b'].data, self.db2data['a2'].two(self.db2)[0].data)

    def test_copy_main_object_with_relation_mix(self):
        self.db1data['b'].copy_to_db(self.db2)
        self.db1data['a1'].copy_to_db(self.db2, self.db)
        self.db1data['a2'].copy_to_db(self.db2, self.db)
        ModelAm2m.clear_cache()
        self.db2data = self.get_elements_from_db(self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertEqual(self.db1data['a2'].data, self.db2data['b'].two(self.db2)[0].data)
        self.assertEqual(1, len(self.db2data['b'].one(self.db2)))
        self.assertEqual(1, len(self.db2data['b'].two(self.db2)))
        self.assertEqual(1, len(self.db2data['a1'].one(self.db2)))
        self.assertEqual(0, len(self.db2data['a1'].two(self.db2)))
        self.assertEqual(0, len(self.db2data['a2'].one(self.db2)))
        self.assertEqual(1, len(self.db2data['a2'].two(self.db2)))
        self.assertEqual(self.db1data['b'].data, self.db2data['a1'].one(self.db2)[0].data)
        self.assertEqual(self.db1data['b'].data, self.db2data['a2'].two(self.db2)[0].data)

    def test_copy_main_object_with_relation_mix2(self):
        self.db1data['b'].copy_to_db(self.db2)
        self.db1data['a1'].copy_to_db(self.db2, self.db)
        self.db1data['a2'].copy_to_db(self.db2)
        ModelAm2m.clear_cache()
        self.db2data = self.get_elements_from_db(self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertEqual(1, len(self.db2data['b'].one(self.db2)))
        self.assertEqual(0, len(self.db2data['b'].two(self.db2)))
        self.assertEqual(1, len(self.db2data['a1'].one(self.db2)))
        self.assertEqual(0, len(self.db2data['a1'].two(self.db2)))
        self.assertEqual(0, len(self.db2data['a2'].one(self.db2)))
        self.assertEqual(0, len(self.db2data['a2'].two(self.db2)))
        self.assertEqual(self.db1data['b'].data, self.db2data['a1'].one(self.db2)[0].data)

    def test_raw_save(self):
        self.db1data['b'].save(self.db2)
        self.db1data['a1'].save(self.db2)
        self.db1data['a2'].save(self.db2)
        ModelAm2m.clear_cache()
        self.db2data = self.get_elements_from_db(self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual(self.db1data['a1'].data, ModelAm2m.get(self.initdata['a1'].id, self.db2).data)
        self.assertEqual(self.db1data['a2'].data, ModelAm2m.get(self.initdata['a2'].id, self.db2).data)
        self.assertEqual(0, len(self.db2data['b'].one(self.db2)))
        self.assertEqual(0, len(self.db2data['b'].two(self.db2)))
        self.assertEqual(0, len(self.db2data['a1'].one(self.db2)))
        self.assertEqual(0, len(self.db2data['a1'].two(self.db2)))
        self.assertEqual(0, len(self.db2data['a2'].one(self.db2)))
        self.assertEqual(0, len(self.db2data['a2'].two(self.db2)))

    def test_parallel_save(self):
        for key, obj in self.db1data.items():
            obj.copy_to_db(self.db2, self.db)
            obj.data *= 2
            obj.save(self.db)

        ModelAm2m.clear_cache()

        self.db2data = self.get_elements_from_db(self.db2)
        self.assertNotEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertNotEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertNotEqual(self.db1data['a2'].data, self.db2data['b'].two(self.db2)[0].data)

        for key, obj in self.db1data.items():
            obj.save(self.db2)

        ModelAm2m.clear_cache()

        self.db2data = self.get_elements_from_db(self.db2)
        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertEqual(self.db1data['a2'].data, self.db2data['b'].two(self.db2)[0].data)
