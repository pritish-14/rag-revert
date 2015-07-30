# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
import xlwt


class exit_wiz(osv.osv):
    _name = 'exit.wiz'

    '''_columns = {
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),   
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'exit.wiz', context=c),
        }'''    


    def print_report_exit(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        contract_obj = self.pool.get('exit')
        data = self.read(cr, uid, ids, context=context)[0]
        contract_ids = contract_obj.search(cr, uid, [], context=context) or []
        datas = {
             'ids': contract_ids,
             'model': 'exit',
#             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'exit_aeroo_report',
            'datas': datas,
        }

''' def print_report_exit(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        ir_model_data = self.pool.get('ir.model.data')
        template_id = ir_model_data.get_object_reference(cr, uid, 'employee_exit', 'exit_aeroo_report.ods')[1]            
        for data in self.browse(cr, uid, ids, context=context):
            date_start = data.date_start
            date_end = data.date_end
            
        
        return {
            'name': _('Exit Report'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'exit',
            'type': 'ir.actions.act_window',
            'view_id': template_id,
            'domain': [('date_start','>=',date_start),('date_end','<=',date_end)],
        }'''
