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

    def print_report_probation(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        contract_obj = self.pool.get('hr.contract')
        data = self.read(cr, uid, ids, context=context)[0]
        contract_ids = contract_obj.search(cr, uid, [], context=context) or []
        datas = {
             'ids': contract_ids,
             'model': 'hr.contract',
#             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'probation_aeroo_report_xls',
            'datas': datas,
        }

