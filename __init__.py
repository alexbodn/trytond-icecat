# -*- coding: utf-8 -*-
'''

    icecat

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''

from trytond.pool import Pool
from product import ImportIcecatProduct, AddIcecatProductView, Product
from language import Language


def register():
    """
    Register classes
    """
    Pool.register(
        Product,
        AddIcecatProductView,
        Language,
        module='product_icecat', type_='model'
    )
    Pool.register(
        ImportIcecatProduct,
        module='product_icecat', type_='wizard'
    )
