import unittest
import logging
from .model import ModelTest
from .intfield import IntFieldTest
from .stringfield import StringFieldTest
from .listfield import ListFieldTest
from .one_to_one_relation import OneToOneRelationTest
from .one_to_many_relation import OneToManyRelationTest
from .many_to_many_relation import ManyToManyRelationTest
from .one_to_many_subname_relation import OneToManySubnameRelationTest
from .datefield import DateFieldTest
from .datetimefield import DateTimeFieldTest
from .multidatabase import MultiDatabaseTest
from .multidatabase_o2o import MultiDatabaseO2OTest
from .multidatabase_o2m import MultiDatabaseO2MTest
from .multidatabase_m2m import MultiDatabaseM2MTest
from .no_init_db import NoInitDbTest

all_test_cases = [
    ModelTest,
    IntFieldTest,
    StringFieldTest,
    OneToOneRelationTest,
    OneToManyRelationTest,
    ManyToManyRelationTest,
    OneToManySubnameRelationTest,
    DateFieldTest,
    DateTimeFieldTest,
    MultiDatabaseTest,
    MultiDatabaseO2OTest,
    MultiDatabaseO2MTest,
    MultiDatabaseM2MTest,
    ListFieldTest,
    NoInitDbTest,
]


def get_all_test_suite():
    logging.basicConfig(level=logging.INFO, format="%(asctime)-15s:%(message)s", filename='test.log')
    logging.getLogger('cdborm').info('\n\t*** TESTING STARTED ***')
    suite = unittest.TestLoader()
    prepered_all_test_cases = []
    for test_case in all_test_cases:
        prepered_all_test_cases.append(
            suite.loadTestsFromTestCase(test_case)
        )
    return unittest.TestSuite(prepered_all_test_cases)
