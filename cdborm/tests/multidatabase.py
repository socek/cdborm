from .base import CdbOrmMultiDbTestCase

from cdborm.model import Model
from cdborm import fields


class ModelASimple(Model):
    string = fields.StringField()
    integer = fields.IntField()


class MultiDatabaseTest(CdbOrmMultiDbTestCase):

    def test_simple_values_save(self):

        obj = ModelASimple()
        obj.string = 'str'
        obj.integer = 10
        obj.save(self.db)

        ModelASimple.clear_cache()

        obj_a = ModelASimple.get(obj.id, self.db)
        obj_a.save(self.db2)
        obj_a.save(self.db2)

        ModelASimple.clear_cache()

        obj_b = ModelASimple.get(obj.id, self.db2)

        for test_obj in [obj_a, obj_b]:
            for key in ['id', 'string', 'integer']:
                self.assertEqual(getattr(obj, key), getattr(test_obj, key))
            self.assertNotEqual(obj._rev_cache[id(self.db)], test_obj._rev_cache[id(self.db2)])

    def test_simple_values_copy(self):
        obj = ModelASimple()
        obj.string = 'str'
        obj.integer = 10
        obj.save(self.db)

        ModelASimple.clear_cache()

        obj_a = ModelASimple.get(obj.id, self.db)
        obj_a.copy_to_db(self.db2)
        obj_a.copy_to_db(self.db2)

        ModelASimple.clear_cache()

        obj_b = ModelASimple.get(obj.id, self.db2)

        for test_obj in [obj_a, obj_b]:
            for key in ['id', 'string', 'integer']:
                self.assertEqual(getattr(obj, key), getattr(test_obj, key))
            self.assertNotEqual(obj._rev_cache[id(self.db)], test_obj._rev_cache[id(self.db2)])

    def test_simple_values_copy2(self):
        obj = ModelASimple()
        obj.string = 'str'
        obj.integer = 10
        obj.save(self.db)

        ModelASimple.clear_cache()

        obj_a = ModelASimple.get(obj.id, self.db)
        obj_a.copy_to_db(self.db2, self.db)
        obj_a.copy_to_db(self.db2, self.db)

        ModelASimple.clear_cache()

        obj_b = ModelASimple.get(obj.id, self.db2,)

        for test_obj in [obj_a, obj_b]:
            for key in ['id', 'string', 'integer']:
                self.assertEqual(getattr(obj, key), getattr(test_obj, key))
            self.assertNotEqual(obj._rev_cache[id(self.db)], test_obj._rev_cache[id(self.db2)])
