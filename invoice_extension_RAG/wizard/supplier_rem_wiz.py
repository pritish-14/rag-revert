# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
import xlwt


class account_voucher_supplier(osv.osv):
    _name = 'account.voucher.supplier'

    def print_supplier_remittance(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        voucher_obj = self.pool.get('account.voucher')
        data = self.read(cr, uid, ids, context=context)[0]
        voucher_ids = voucher_obj.search(cr, uid, [], context=context) or []
        datas = {
             'ids': voucher_ids,
             'model': 'account.voucher',
#             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'supplier_aeroo_report_xls',
            'datas': datas,
        }

class partner_statement_wiz(osv.osv):
    _name = 'partner.statement.wiz'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'brand_id': fields.many2one('brand', 'Brand'),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),        
    }
    
    _defaults = {
        'date_start': fields.date.context_today,

    }

    def print_partner_statement(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
#        invoice_obj = self.pool.get('partner.statement.wiz')
        data = self.read(cr, uid, ids, context=context)[0]
        invoice_ids = self.browse(cr, uid, ids, context)
        print "invoice_ids", ids
        datas = {
             'ids': ids,
             'model': 'partner.statement.wiz',
#             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'partner_statement_aeroo_report_xls',
            'datas': datas,
        }

