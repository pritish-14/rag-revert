# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
import xlwt


class probation_wiz(osv.osv):
    _name = 'payslip.wiz'

    def print_report_payslip(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        contract_obj = self.pool.get('hr.payroll.register')
        data = self.read(cr, uid, ids, context=context)[0]
        contract_ids = contract_obj.search(cr, uid, [], context=context) or []
        datas = {
             'ids': contract_ids,
             'model': 'hr.payroll.register',
#             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr_payroll_register_report',
            'datas': datas,
        }

