# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
import xlwt


class payroll_wiz(osv.osv):
    _name = 'payroll.report.wiz'

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
                rule_id = self.pool.get('hr.salary.rule').search(cr, uid, [('name', '=', 'PAYE')])
                print "rule", rule_id
                rule = self.pool.get('hr.salary.rule').browse(cr, uid, rule_id)                
                template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'view_hr_payslip_line_paye_deduct_tree')[1]            
                return {
                    'name': _('PAYE Deductions'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip.line',
                    'type': 'ir.actions.act_window',
                    'view_id': template_id,
                    'domain': [('company_id','=',company_id),('name','=',rule.name),('category_id','=',rule.category_id.id)],
                }
            elif report_name == 'nhif':             
                template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'view_hr_payslip_line_nhif_tree')[1]            
                rule_id = self.pool.get('hr.salary.rule').search(cr, uid, [('name', '=', 'NHIF')])
                print "rule", rule_id
                rule = self.pool.get('hr.salary.rule').browse(cr, uid, rule_id)                
                return {
                    'name': _('NHIF Deductions'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip.line',
                    'type': 'ir.actions.act_window',
                    'view_id': template_id,
                    'domain': [('company_id','=',company_id),('name','=',rule.name),('category_id','=',rule.category_id.id)],
                }                                
            elif report_name == 'icea_deduct':
                template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'view_hr_payslip_line_common_tree')[1]            
                rule_id = self.pool.get('hr.salary.rule').search(cr, uid, [('name', '=', 'ICEA')])
                print "rule", rule_id
                rule = self.pool.get('hr.salary.rule').browse(cr, uid, rule_id)                
                return {
                    'name': _('ICEA Deductions'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip.line',
                    'type': 'ir.actions.act_window',
                    'view_id': template_id,
                    'domain': [('company_id','=',company_id),('name','=',rule.name),('category_id','=',rule.category_id.id)]
                }                                            
            elif report_name == 'icea_endow':
                template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'view_hr_payslip_line_common_tree')[1]            
                rule_id = self.pool.get('hr.salary.rule').search(cr, uid, [('name', '=', 'ICEA Endowment')])
                print "rule", rule_id
                rule = self.pool.get('hr.salary.rule').browse(cr, uid, rule_id)                
                return {
                    'name': _('ICEA Endowment Deductions'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip.line',
                    'type': 'ir.actions.act_window',
                    'view_id': template_id,
                    'domain': [('company_id','=',company_id),('name','=',rule.name),('category_id','=',rule.category_id.id)]
                }                                            
            elif report_name == 'qweb_sacco':
                template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'view_hr_payslip_line_common_tree')[1]            
                rule_id = self.pool.get('hr.salary.rule').search(cr, uid, [('name', '=', 'Q/Way Sacco')])
                print "rule", rule_id
                rule = self.pool.get('hr.salary.rule').browse(cr, uid, rule_id)                
                return {
                    'name': _('Q/Way Sacco Deductions'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip.line',
                    'type': 'ir.actions.act_window',
                    'view_id': template_id,
                    'domain': [('company_id','=',company_id),('name','=',rule.name),('category_id','=',rule.category_id.id)]
                }
            elif report_name == 'stanbic_loan':
                template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'view_hr_payslip_line_common_tree')[1]            
                rule_id = self.pool.get('hr.salary.rule').search(cr, uid, [('name', '=', 'Stanbic Loan Deductions')])
                print "rule", rule_id
                rule = self.pool.get('hr.salary.rule').browse(cr, uid, rule_id)                
                return {
                    'name': _('Stanbic Loan Deductions'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip.line',
                    'type': 'ir.actions.act_window',
                    'view_id': template_id,
                    'domain': [('company_id','=',company_id),('name','=',rule.name),('category_id','=',rule.category_id.id)]
                }                                                                                                                                                                        
