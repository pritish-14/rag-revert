# Copyright (c) 2015: Apagen Solutions (P) Ltd.

from openerp.osv import fields, osv

class Brand(osv.osv):
	_name = 'brand'
	_columns = {
        'name': fields.char("Name"),
        'type': fields.selection([
                ('1', "Radio"),
                ('2', 'TV'),
                ('3', 'Digital')
            ], "Type", required='True'),

		'company_id': fields.many2one(
		    'res.company', 'Company', required=True, select=1),
    }
    

