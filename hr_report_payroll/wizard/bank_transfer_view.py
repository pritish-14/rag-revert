# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
import xlwt

class hr_payslip_line(osv.osv):
    '''
    Payslip Line
    '''

    _inherit = 'hr.payslip.line'
    _columns = {
        'employee_id': fields.related('slip_id','employee_id', type='many2one', relation='hr.employee', string="Employee"),    
        'staff_no': fields.related('employee_id','staff_no', type='integer', string="Staff No"),
        'company_id': fields.related('slip_id','company_id', type='many2one', relation='res.company', string="Company"), 
        'nhif_no': fields.related('employee_id','nhif_no', type='integer', string="NHIF Card Number"),           
        'pin_no': fields.related('employee_id','pin_no', type='integer', string="PIN"),           
        'birthday': fields.related('employee_id','birthday', type='date', string="Date of Birth"),
        'account_no': fields.related('employee_id','bank_account_id', type='many2one', relation='res.partner.bank', string="Account No"),
        'bank_name_': fields.related('account_no','bank_name', type='char', string="Bank Name"),
        'bank_code': fields.related('account_no','bank_bic', type='char', string="Bank Code"),                          
    }





class bank_wiz(osv.osv):
    _name = 'bank.wiz'

    _columns = {
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),
           
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'bank.wiz', context=c),
        }    

    def print_report_bank(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        ir_model_data = self.pool.get('ir.model.data')
        template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'hr_bank_report_view_tree')[1]            
        for data in self.browse(cr, uid, ids, context=context):
            date_start = data.date_start
            date_end = data.date_end
            
        
        return {
            'name': _('Bank’s Report'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.payslip.line',
            'type': 'ir.actions.act_window',
            'view_id': template_id,
            'domain': [('name','=','Net')],
            #'domain': [('date_start','>=',date_start),('date_end','<=',date_end)],
        }
