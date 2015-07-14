from datetime import datetime, timedelta
import time
import datetime
from openerp.osv import fields, osv


class purchase_requisition(osv.osv):
	_inherit = "purchase.requisition"
	_description = "Purchase Requisition"
 

	_columns = {
        'name': fields.char('Call for Bids Reference'),
		'creation_date': fields.datetime('Creation Date',required=True,readonly=True),
		'user_id': fields.many2one('res.users', 'Responsible',required=True),
		
	}
	_defaults = {
		'creation_date': datetime.datetime.now(),
	}

	
	
class purchase_requisition(osv.osv):
    _inherit = "purchase.order"
    #_description = "Purchase Requisition"
 

    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('approval', 'Awating Finance Approval'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ]

    def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
        res = super(purchase_requisition, self)._prepare_invoice(cr, uid, order, line_ids, context=context)
        res.update({'date_invoice':datetime.datetime.now()})
        print res
        
        return res


	_columns = {
	
			'state': fields.selection(STATE_SELECTION, 'Status', readonly=True,
                                  help="The status of the purchase order or the quotation request. "
                                       "A request for quotation is a purchase order in a 'Draft' status. "
                                       "Then the order has to be confirmed by the user, the status switch "
                                       "to 'Confirmed'. Then the supplier must confirm the order to change "
                                       "the status to 'Approved'. When the purchase order is paid and "
                                       "received, the status becomes 'Done'. If a cancel action occurs in "
                                       "the invoice or in the receipt of goods, the status becomes "
                                       "in exception.",
                                  select=True, copy=False),
			'create_uid': fields.many2one('res.users', 'Responsible',required=True),
	
	}
	
	_defaults = {
		'create_uid': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id,
	}
	
	def wkf_approval_received(self, cr, uid, ids):
		#print"------------"
		self.write(cr, uid, ids, { 'state' : 'approval' })
		return True
		
		
		
	
	
