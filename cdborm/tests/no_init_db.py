from tempfile import NamedTemporaryFile

from .base import CdbOrmTestCase
from cdborm.connection import connec_to_database
from cdborm.model import Model

class MyModelNoInitDB(Model):
    pass

class NoInitDbTest(CdbOrmTestCase):

    def setUp(self):
        path = NamedTemporaryFile().name
        self.db, inited = connec_to_database(path)

    def test_all(self):
        model = MyModelNoInitDB()
        model.save(self.db)

        model.clear_cache()

        self.assertEqual(model.id, MyModelNoInitDB.all(self.db)[0].id)

    def test_save_and_get(self):
        model = MyModelNoInitDB()
        model.save(self.db)

        model.clear_cache()

        self.assertEqual(model.id, MyModelNoInitDB.get(model.id, self.db).id)
