import time
from datetime import datetime
from openerp.osv import fields, osv

class asset_category(osv.osv):
    _inherit = 'account.asset.category'
    _description = 'Asset category'

    _columns = {
        'useful_life_years': fields.float('Useful Life (Years)')
    }

    _defaults = {
        'useful_life_years': 0.0,
    }


class account_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _description = 'Asset'

    _columns = {
    	'act': fields.boolean('Active'),
        'location_id': fields.char('Location',readonly=True, states={'draft':[('readonly',False)]}),
        #'location_id': fields.many2one('stock.location', 'Location'),
        'method': fields.selection([('linear','Linear'),('degressive','Degressive'),('straight_line','Straight Line')], 'Computation Method', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'depreciation_frequency': fields.selection([('yearly','Yearly'),('monthly','Monthly')], 'Depreciation Frequency', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'method_number': fields.integer('Number of Depreciations', readonly=True, states={'draft':[('readonly',False)]}, help="The number of depreciations needed to depreciate your asset"),
        'method_period': fields.integer('Number of Months in a Period', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The amount of time between two depreciations, in months"),
        
        #'method_period': fields.integer('Number of Months in a Period'),
        #'method_end': fields.date('Ending Date', readonly=True, states={'draft':[('readonly',False)]}),
        'end_method': fields.date('Ending Date'),
        'method_time': fields.selection([('number','Number of Depreciations'),('end','Ending Date')], 'Time Method', required=True, readonly=True, states={'draft':[('readonly',False)]},
                                  help="Choose the method to use to compute the dates and number of depreciation lines.\n"\
                                       "  * Number of Depreciations: Fix the number of depreciation lines and the time between 2 depreciations.\n" \
                                       "  * Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond."),
        'prorata':fields.boolean('Prorata Temporis', readonly=True, states={'draft':[('readonly',False)]}, help='Indicates that the first depreciation entry for this asset have to be done from the purchase date instead of the first January'),
        'brand_id': fields.many2one('brand', "Brand", readonly=True, states={'draft':[('readonly',False)]}),
    }

    _defaults = {
        #'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'account.asset.asset',context=context),
        'act': True,
        'method': 'straight_line',
        'depreciation_frequency': 'monthly'
    }
    
    
'''    _defaults = {
        'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'account.asset.asset',context=context),
#        'method': 'straight_line',
        'depreciation_frequency': 'monthly'
    }'''
