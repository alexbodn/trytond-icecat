# -*- coding: utf-8 -*-
'''

    Add icecat id to language

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: BSD, see LICENSE for more details

'''
from trytond.pool import PoolMeta
from trytond.model import fields

__all__ = ['Language']
__metaclass__ = PoolMeta


class Language:
    __name__ = 'ir.lang'

    icecat_id = fields.Integer('Icecat ID')
