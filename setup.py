# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
import sys

install_requires=[
    'CodernityDB',
]

dependency_links = [
]

if __name__ == '__main__':
    setup(name='CodernityDB-orm',
        version='0.1.1',
        description="ORM for CodernityDB.",
        author='Dominik "Socek" Długajczyk',
        author_email='msocek@gmail.com',
        packages=find_packages(),
        install_requires=install_requires,
        dependency_links=dependency_links,
        test_suite = 'cdborm.tests.get_all_test_suite',
    )
