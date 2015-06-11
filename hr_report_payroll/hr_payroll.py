
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval

class hr_payslip_line(osv.osv):
    _inherit = 'hr.payslip.line'

    def _calculate_total(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = float(line.quantity) * line.amount * line.rate / 100
        return res
    
    _columns = {
        'employee_id': fields.related('slip_id','employee_id', type='many2one', relation='hr.employee', string="Employee"),    
        'staff_no': fields.related('employee_id','staff_no', type='integer', string="Staff No"),
        'company_id': fields.related('slip_id','company_id', type='many2one', relation='res.company', string="Company"), 
        'total': fields.function(_calculate_total, method=True, type='float', string='Amount', digits_compute=dp.get_precision('Payroll'),store=True ),
        'employee_id': fields.related('slip_id', 'employee_id', type='many2one', relation='hr.employee', string="Employee"),    
        'staff_no': fields.related('employee_id', 'staff_no', type='integer', string="Staff No"),
        'company_id': fields.related('slip_id', 'company_id', type='many2one', relation='res.company', string="Company"), 
        'nhif_no': fields.related('employee_id','nhif_no', type='integer', string="NHIF Card Number"),           
        'pin_no': fields.related('employee_id', 'pin_no', type='integer', string="PIN"),           
        'birthday': fields.related('employee_id', 'birthday', type='date', string="Date of Birth"),                           
    }
    
class payslip(osv.osv):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _columns = {
        'user_id': fields.many2one('res.users', 'Responsible'),
    }        
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def send_payslip_email(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        #res = super(payslip, self).send_payslip_email(cr, uid, ids, context)
        #assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'email_template_edi_hr_payslip')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'hr.payslip',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        print "..............", ctx
        return ctx


