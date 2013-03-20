from .base import CdbOrmMultiDbTestCase

from cdborm.model import Model
from cdborm import relation
from cdborm import fields


class ModelAo2m(Model):
    one = relation.OneToMany('ModelBo2m')
    two = relation.OneToMany('ModelBo2m', 'name2')
    data = fields.IntField()


class ModelBo2m(Model):
    one = relation.OneToManyList('ModelAo2m')
    two = relation.OneToManyList('ModelAo2m', 'name2')
    data = fields.IntField()


class MultiDatabaseO2MTest(CdbOrmMultiDbTestCase):
    def setUp(self):
        def init_objects():
            data = {}

            data['a1'] = ModelAo2m()
            data['a1'].data = 1
            data['a1'].save(self.db)

            data['a2'] = ModelAo2m()
            data['a2'].data = 2
            data['a2'].save(self.db)

            data['b'] = ModelBo2m()
            data['b'].one.assign(data['a1'])
            data['b'].two.assign(data['a2'])
            data['b'].data = 10
            data['b'].save(self.db)

            return data

        super(MultiDatabaseO2MTest, self).setUp()
        self.initdata = init_objects()
        ModelAo2m.clear_cache()

        self.db1data = self.get_elements_from_db(self.db)
        ModelAo2m.clear_cache()

        self.db2data = {}

    def get_elements_from_db(self, db):
        return {
            'a1': ModelAo2m.get(self.initdata['a1'].id, db),
            'a2': ModelAo2m.get(self.initdata['a2'].id, db),
            'b': ModelBo2m.get(self.initdata['b'].id, db),
        }

    def test_copy_main_object(self):
        self.db1data['b'].copy_to_db(self.db2)
        ModelAo2m.clear_cache()
        self.db2data['b'] = ModelBo2m.get(self.initdata['b'].id, self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual([], self.db2data['b'].one(self.db2))
        self.assertEqual([], self.db2data['b'].two(self.db2))

    def test_copy_main_object_with_relation(self):
        self.db1data['b'].copy_to_db(self.db2, self.db)
        ModelAo2m.clear_cache()
        self.db2data['b'] = ModelBo2m.get(self.initdata['b'].id, self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual([], self.db2data['b'].one(self.db2))
        self.assertEqual([], self.db2data['b'].two(self.db2))

    def test_copy_subobject_object_with_relation(self):
        self.db1data['b'].copy_to_db(self.db2, self.db)
        self.db1data['a1'].copy_to_db(self.db2, self.db)
        self.db1data['a2'].copy_to_db(self.db2, self.db)
        ModelAo2m.clear_cache()
        self.db2data = self.get_elements_from_db(self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertEqual(self.db1data['a2'].data, self.db2data['b'].two(self.db2)[0].data)
        self.assertEqual(1, len(self.db2data['b'].one(self.db2)))
        self.assertEqual(1, len(self.db2data['b'].two(self.db2)))
        self.assertEqual(self.db1data['b'].data, self.db2data['a1'].one(self.db2).data)
        self.assertEqual(self.db1data['b'].data, self.db2data['a2'].two(self.db2).data)

    def test_copy_main_object_with_relation_mix(self):
        self.db1data['b'].copy_to_db(self.db2)
        self.db1data['a1'].copy_to_db(self.db2, self.db)
        self.db1data['a2'].copy_to_db(self.db2, self.db)
        ModelAo2m.clear_cache()
        self.db2data = self.get_elements_from_db(self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertEqual(self.db1data['a2'].data, self.db2data['b'].two(self.db2)[0].data)
        self.assertEqual(1, len(self.db2data['b'].one(self.db2)))
        self.assertEqual(1, len(self.db2data['b'].two(self.db2)))
        self.assertEqual(self.db1data['b'].data, self.db2data['a1'].one(self.db2).data)
        self.assertEqual(self.db1data['b'].data, self.db2data['a2'].two(self.db2).data)

    def test_copy_main_object_with_relation_mix2(self):
        self.db1data['b'].copy_to_db(self.db2)
        self.db1data['a1'].copy_to_db(self.db2, self.db)
        self.db1data['a2'].copy_to_db(self.db2)
        ModelAo2m.clear_cache()
        self.db2data = self.get_elements_from_db(self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertEqual(1, len(self.db2data['b'].one(self.db2)))
        self.assertEqual(0, len(self.db2data['b'].two(self.db2)))
        self.assertEqual(self.db1data['b'].data, self.db2data['a1'].one(self.db2).data)

    def test_raw_save(self):
        self.db1data['b'].save(self.db2)
        self.db1data['a1'].save(self.db2)
        self.db1data['a2'].save(self.db2)
        ModelAo2m.clear_cache()
        self.db2data = self.get_elements_from_db(self.db2)

        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual([], self.db2data['b'].one(self.db2))
        self.assertEqual(self.db1data['a1'].data, ModelAo2m.get(self.initdata['a1'].id, self.db2).data)
        self.assertEqual([], self.db2data['b'].two(self.db2))
        self.assertEqual(self.db1data['a2'].data, ModelAo2m.get(self.initdata['a2'].id, self.db2).data)

    def test_parallel_save(self):
        for key, obj in self.db1data.items():
            obj.copy_to_db(self.db2, self.db)
            obj.data *= 2
            obj.save(self.db)

        ModelAo2m.clear_cache()

        self.db2data = self.get_elements_from_db(self.db2)
        self.assertNotEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertNotEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertNotEqual(self.db1data['a2'].data, self.db2data['b'].two(self.db2)[0].data)

        for key, obj in self.db1data.items():
            obj.save(self.db2)

        ModelAo2m.clear_cache()

        self.db2data = self.get_elements_from_db(self.db2)
        self.assertEqual(self.db1data['b'].data, self.db2data['b'].data)
        self.assertEqual(self.db1data['a1'].data, self.db2data['b'].one(self.db2)[0].data)
        self.assertEqual(self.db1data['a2'].data, self.db2data['b'].two(self.db2)[0].data)
