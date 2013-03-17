import unittest
import logging
from .model import ModelTest
from .intfield import IntFieldTest
from .stringfield import StringFieldTest
from .one_to_one_relation import OneToOneRelationTest
from .one_to_many_relation import OneToManyRelationTest
from .many_to_many_relation import ManyToManyRelationTest
from .one_to_many_subname_relation import OneToManySubnameRelationTest
from .multidatabase import MultiDatabaseTest

all_test_cases = [
    ModelTest,
    IntFieldTest,
    StringFieldTest,
    OneToOneRelationTest,
    OneToManyRelationTest,
    ManyToManyRelationTest,
    OneToManySubnameRelationTest,
    MultiDatabaseTest,
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
