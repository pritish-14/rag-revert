from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class product_packages(osv.osv):
    _name = "product.packages"

    _columns = {
        'note': fields.text('Notes'),        
        'name': fields.char('Name'),
        'type': fields.many2one('package.type', 'Type', required=True),
        'brand_id': fields.many2one('brand', 'Brand'),    
        'company_id': fields.many2one('res.company', 'Company', required=True),  
        'created_by': fields.many2one('res.users', 'Created By', readonly='True', select=True, track_visibility='onchange'), 
        'created_on': fields.datetime('Created On', readonly=True),                     
        'modified_by': fields.many2one('res.users', 'Modified By', readonly='True', select=True, track_visibility='onchange'), 
        'modified_on': fields.datetime('Modified On', readonly=True),                     
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'created_by': lambda obj, cr, uid, context: uid, 
        'created_on': fields.datetime.now,    
    }

class package_type(osv.osv):
    _name = "package.type"

    _columns = {
        'name': fields.char('Name', required=True)
    
    }

class package_day(osv.osv):
    _name = "package.day"
    _columns = {
        'name': fields.char('Name', required=True)
    }

class package_timing(osv.osv):
    _name = "package.timing"
    _columns = {
        'name': fields.char('Name', required=True)
    }

class product_packages_line(osv.osv):
    _name = "product.packages.line"

    _columns = {
        'tv_sponsor_type': fields.selection([('daily','Daily'),('chart','Chart'),('show','Show')], 'Sponsorships Type'),       
        'spots_per_day': fields.integer("Spots Per Day"),    
        'banners': fields.integer("Banners"),        
        'spots_per_week': fields.integer("Spots Per Week"),
        'value': fields.char('Value'),
        'show': fields.char('Show'),
        'week': fields.integer('No of Week'),
        'sponsor_type': fields.selection([('monthly','Monthly'),('feature','Feature')], 'Sponsorship Rates'),   
        'promo_type': fields.selection([('breakfast','Breakfast'),('drive','Drive'),('mid','Mid-Morning')], 'Promotion Rates'),           
        'brand_id': fields.many2one('brand', 'Brand'),    
        'line_id': fields.many2one('product.packages', 'Line'),
        'name': fields.char('Package', required=True),
        'mentions': fields.integer('Mentions'),
        'seconds': fields.integer('No of Seconds'),        
        'price': fields.integer('Price'),
        'cost_per_month': fields.integer('Cost Per Month'),
        'cost_per_week': fields.integer('Cost Per Week'),                        
        'timings': fields.many2many('package.timing', 'package_time_rel', 'parent_id', 'child_id', 'Timings'),   
        'days': fields.many2many('package.day', 'package_day_rel', 'parent_id', 'child_id', 'Days'),        
    }

