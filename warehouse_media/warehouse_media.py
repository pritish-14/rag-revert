import time
from datetime import datetime

from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    _columns = {
    	'transfer_by': fields. many2one('res.users', 'Transferred By', readonly=1),
    	'transfer_date': fields.datetime('Transfer Date', readonly=1),
    	'company_id': fields.many2one('res.company', 'Company', required=True, select=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
    	}
    _defaults = {
        #'transfer_date': fields.date.context_today,
        'transfer_by': lambda obj, cursor, user, context: user,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.picking', context=c),
    }
    
    def do_enter_transfer_details(self, cr, uid, picking, context=None):
        if not context:
            context = {}
        print "2222222222222222222222222", context
        #picking_id = self.browse(cr, uid, picking, context)
        self.write(cr, uid, picking, {'transfer_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, context)
        context.update({
            'active_model': self._name,
            'active_ids': picking,
            'active_id': len(picking) and picking[0] or False,
            
        })

        created_id = self.pool['stock.transfer_details'].create(cr, uid, {'picking_id': len(picking) and picking[0] or False}, context)
        return self.pool['stock.transfer_details'].wizard_view(cr, uid, created_id, context)
    
class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    
    _columns = {
    	'responsible': fields.many2one('res.users', 'Responsible', required=1),
    	}
    _defaults = {
    	'responsible': lambda obj, cr, uid, context: uid,
    	}
    	
class calendar_event(osv.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'
    
    _columns = {
    	'status': fields.selection([('1', "Scheduled"), ('2', 'In Progress'), ('3', 'Complete')],
                                 "Status", required='True'),
         }
    
    
