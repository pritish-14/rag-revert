from openerp import tools
from openerp.osv import fields, osv


class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'
    
    def _cal_total_invoice(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total_invoice=0.0
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'invoiced_target' : 0.0
            }
            val5 = 0.0
           
            
            for line in order.team_meber_id:
                total_invoice = total_invoice + line.monthly_target
                #val5 = val5 + total_volume
            res[order.id] =  total_invoice
        return res
    
    _columns = {
        'time_oreder': fields.boolean('Time Order'),
        'space_oreder': fields.boolean('Space Order'),
        'invoices_id': fields.boolean('Invoices'),
        'invoiced_target': fields.function(_cal_total_invoice, string='Invoice Target',readonly=True,
            help="Target of invoice revenue for the current month. This is the amount the sales \n"
                    "team estimates to be able to invoice this month."),
        'team_meber_id':fields.one2many('team.member','name','Team Members'),
    }
    
    
    _defaults = {
        'time_oreder': True,
        'space_oreder': True,
        'invoices_id': True,
    }
    
    
    


class Induction(osv.osv):
	_name = 'team.member'
	#_rec_name='company_id'
	
	_columns = {
	
		'name': fields.many2one('crm.case.section','Name'),
		'name_id': fields.many2one('res.users','Name',required=True),
		'monthly_target': fields.float('Monthly Targets', required=True),
		'allowed_discount': fields.integer('Allowed Discount (%)', required=True),
		}		
