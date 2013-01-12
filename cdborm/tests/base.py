import unittest
from tempfile import NamedTemporaryFile
from cdborm.connection import connec_to_database

class CdbOrmTestCase(unittest.TestCase):
    def setUp(self):
        path = NamedTemporaryFile().name
        self.db, inited = connec_to_database(path, True)
