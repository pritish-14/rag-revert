from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc


'''class acconting_move(osv.osv):
    _inherit = 'account.move'
    _columns = {
    	
    	'brand_id': fields.many2one('brand', 'Brand'),
    }'''
    
    
class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _columns = {
    	
    	'brand_id': fields.many2one('brand', 'Brand'),
    }
