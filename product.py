# -*- coding: utf-8 -*-
'''

    icecat

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: BSD, see LICENSE for more details

'''
from decimal import Decimal

from trytond.wizard import Wizard, StateView, Button, StateAction
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.exceptions import UserError
from trytond.transaction import Transaction
from trytond.config import config
from trytond.pyson import Eval
from lxml import objectify
import requests


__all__ = [
    'AddIcecatProductView', 'ImportIcecatProduct', 'Product',
]
__metaclass__ = PoolMeta


class Product:
    __name__ = 'product.product'

    def save_icecat_alternate_lang_data(self, language, data):
        """
        Extract alternate langauge data from the xml and save it

        :param lanaguge: Active record of the language
        :param data: lxml objectified record of the product
        """
        with Transaction().set_context(language=language.code):
            try:
                expression = '//ProductDescription[@langid="%d"]'
                prod_description, = data.Product.xpath(
                    expression % language.icecat_id
                )
            except ValueError:
                pass
            else:
                self.write(
                    [self],
                    {'description': prod_description.attrib.get('LongDesc')}
                )

    @classmethod
    def create_from_icecat_data(cls, data):
        """
        Create a product from the given XML data object

        :param data: Objectified XML data for a specific product
        """
        Template = Pool().get('product.template')
        IrLang = Pool().get('ir.lang')
        UOM = Pool().get('product.uom')

        unit, = UOM.search([('symbol', '=', 'u')])

        with Transaction().set_context(language='en_US'):
            # Create the product first
            template, = Template.create([{
                'name': data.Product.attrib['Title'],

                # Assume it is units
                'default_uom': unit,

                # List and cost price is not obtained from here
                'cost_price': Decimal('0'),
                'list_price': Decimal('0'),

                # Do not create variants
                'products': [],
            }])

            # get the description in en_US from ProductDescription
            # attribute
            try:
                expression = '//ProductDescription[@langid="1"]'
                prod_description, = data.Product.xpath(expression)
            except ValueError:
                description = None
            else:
                description = prod_description.attrib.get('LongDesc')

            product, = cls.create([{
                'template': template.id,
                'code': data.Product.attrib['Prod_id'],
                'description': description,
            }])

        # Set the translations for translatable fields
        languages = IrLang.search([
            ('translatable', '=', True),
            ('icecat_id', '!=', None),
        ])
        for lanuage in languages:
            product.save_icecat_alternate_lang_data(lanuage, data)

        return product


class AddIcecatProductView(ModelView):
    "Add IceCat product view"
    __name__ = "product.icecat.import.start"

    mode = fields.Selection([
        ('url', 'XML URL'),
        ('product_id', 'Product ID'),
    ], 'Mode', required=True)
    url = fields.Char(
        'XML URL', states={
            'required': Eval('mode') == 'url',
            'invisible': Eval('mode') != 'url',
        }
    )
    product_id = fields.Integer(
        'Product ID', states={
            'required': Eval('mode') == 'product_id',
            'invisible': Eval('mode') != 'product_id',
        }
    )

    @staticmethod
    def default_mode():
        return 'product_id'


class ImportIcecatProduct(Wizard):
    "Import a product from Icecat"
    __name__ = "product.icecat.import"

    start = StateView(
        "product.icecat.import.start",
        "product_icecat.import_start_view_form", [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Import', 'import_', 'tryton-ok', default=True),
        ]
    )
    import_ = StateAction('product.act_product_form')

    @classmethod
    def get_objectified_xml(cls, url):
        """
        Return the objectified XML for the url
        """
        icecat_username = config.get('options', 'icecat_username')
        icecat_password = config.get('options', 'icecat_password')
        if not (icecat_username and icecat_password):
            raise UserError('Icecat username or password not in config')

        return objectify.fromstring(
            requests.get(
                url,
                auth=(icecat_username, icecat_password)
            ).content
        )

    def do_import_(self, action):
        """
        Import the product and close the wizard

        TODO: Take the user to the imported product
        """
        Product = Pool().get('product.product')

        if self.start.mode == 'url':
            url = self.start.url
        elif self.start.mode == 'product_id':
            url = 'http://data.icecat.biz/export/freexml/INT/%d.xml' % (
                self.start.product_id
            )
        data = self.get_objectified_xml(url)

        product = Product.create_from_icecat_data(data)
        action['views'].reverse()
        return action, {'res_id': [product.id]}
