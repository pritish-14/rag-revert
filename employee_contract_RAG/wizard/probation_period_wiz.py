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
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),   
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'probation.wiz', context=c),
        }    

    def print_report_probation(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        ir_model_data = self.pool.get('ir.model.data')
        template_id = ir_model_data.get_object_reference(cr, uid, 'employee_contract_RAG', 'hr_contract_report_view_tree')[1]            
        for data in self.browse(cr, uid, ids, context=context):
            date_start = data.date_start
            date_end = data.date_end
            
        
        return {
            'name': _('Probationer’s Report'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.contract',
            'type': 'ir.actions.act_window',
            'view_id': template_id,
            'domain': [('date_start','>=',date_start),('date_end','<=',date_end)],
        }
