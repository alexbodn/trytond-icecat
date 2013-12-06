# -*- coding: utf-8 -*-
"""
    test_views_depends

    Test tryton views and fields dependency.

    :copyright: (C) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))
import unittest

from lxml import objectify
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction


class TestProduct(unittest.TestCase):
    '''
    Test product
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('product_icecat')

    def test0010import(self):
        '''
        Test import with simple values
        '''
        Product = POOL.get('product.product')
        IRLang = POOL.get('ir.lang')

        dir = os.path.dirname(__file__)
        objectified_xml = objectify.fromstring(
            open(os.path.join(dir, 'simple_product.xml')).read()
        )

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            # set german as translatable
            de_de, = IRLang.search([('code', '=', 'de_DE')])
            de_de.translatable = True
            de_de.icecat_id = 4
            de_de.save()

            # Import the product
            product = Product.create_from_icecat_data(objectified_xml)

            # Test if both translated values got saved
            with Transaction().set_context(language='en_US'):
                product = Product(product.id)
                self.assertEqual(
                    product.name, 'ASUS UX31 ZENBOOK UX31E-RY018X'
                )
                self.assertTrue(
                    'practical and attractive' in product.description
                )
            with Transaction().set_context(language='de_DE'):
                product = Product(product.id)
                self.assertEqual(
                    product.name, 'ASUS UX31 ZENBOOK UX31E-RY018X'
                )
                self.assertTrue(
                    'praktische Vorteile und sieht zum' in product.description
                )


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestProduct)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
