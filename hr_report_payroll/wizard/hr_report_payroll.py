# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
import xlwt


class probation_wiz(osv.osv):
    _name = 'probation.wiz'

    _columns = {
        'report_name': fields.selection([
            ('paye_deduct', 'PAYE Deductions'),
            ('nhif', 'NHIF'),
            ('fbt', 'Fringe Benefit Tax'),
            ('icea_deduct', 'ICEA Deductions'),
            ('icea_endow', 'ICEA Endowment'),
            ('qweb_sacco', 'Q/way Sacco'),
            ('stanbic_loan', 'Stanbic Loan'),
            ], 'Report Name', select=True),
    
        'company_id':fields.many2one('res.company', 'Company', required=True),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'probation.wiz', context=c),
        }    

    def print_report_payroll(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        ir_model_data = self.pool.get('ir.model.data')
        for data in self.browse(cr, uid, ids, context=context):
            company_id = data.company_id.id
            report_name = data.report_name
            if report_name == 'paye_deduct':             
                template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'view_hr_payslip_line_paye_deduct_tree')[1]            
                return {
                    'name': _('Report'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip.line',
                    'type': 'ir.actions.act_window',
                    'view_id': template_id,
                    'domain': [('company_id','=',company_id)('name','=','PAYE')],
                }
            elif report_name == 'nhif':             
                template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'view_hr_payslip_line_nhif_tree')[1]            
                return {
                    'name': _('Report'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip.line',
                    'type': 'ir.actions.act_window',
                    'view_id': template_id,
                    'domain': [('company_id','=',company_id)('name','=','NHIF')],
                }                                
            else:
                template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'view_hr_payslip_line_common_tree')[1]            
                return {
                    'name': _('Report'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip.line',
                    'type': 'ir.actions.act_window',
                    'view_id': template_id,
                    'domain': [('company_id','=',company_id)],
                }                                            
                
