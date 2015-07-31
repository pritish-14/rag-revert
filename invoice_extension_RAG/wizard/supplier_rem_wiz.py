# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
import xlwt


class Supplier_Remittance_Invoice(osv.osv):
    _name = 'supplier.remittance.invoice'

    def print_supplier_remittance(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        print context
        voucher_obj = self.pool.get('account.invoice')
        data = self.read(cr, uid, ids, context=context)[0]
        invoice_obj = self.browse(cr, uid, ids, context=context)
        date_from = invoice_obj.date_from
        date_to = invoice_obj.date_to
        supplier_id = invoice_obj.supplier_id
        print supplier_id.id
        
        if(date_from or date_to):
            if(date_from == None):
                date_from = datetime.datetime.now()
            if(date_to == None):
                date_to = datetime.datetime.now()
            
            voucher_ids = voucher_obj.search(cr, uid,[('partner_id', '=', supplier_id.id),('state', 'in',('draft','paid')),   ('date_invoice', 'in', (date_from,date_to))], context=context) or []
            
        else:
            voucher_ids = voucher_obj.search(cr, uid,[('partner_id', '=', supplier_id.id),('state', 'in',('draft','paid'))], context=context) or []
        
        datas = {
             'ids': voucher_ids,
             'model': 'account.invoice',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'supplier_aeroo_report_xls',
            'datas': datas,
        }
        
        
    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain=[('supplier','=','True')]),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'state': fields.selection([
            ('paid', 'Paid'),
            ('pending', 'Pending'),
            ('both', 'Both'),
            ], 'State', required="True")
    }

class partner_statement_wiz(osv.osv):
    _name = 'partner.statement.wiz'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'brand_id': fields.many2one('brand', 'Brand', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),   
        'invoice_ids': fields.one2many('account.invoice', 'partner_statement_id', "Partner Invoices"),
        'invoices_many_ids': fields.many2many('account.invoice', 'account_partner_rel_id', 'partner_id', 'invoice_id', 'Customer Invoices'),
        
    }
    
    _defaults = {
        'date_start': fields.date.context_today,

    }

    def print_partner_statement(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        ir_model_data = self.pool.get('ir.model.data')
        template_id = ir_model_data.get_object_reference(cr, uid, 'invoice_extension_RAG', 'invoice_report_tree')[1]            
        for data in self.browse(cr, uid, ids, context=context):
            date_start = data.date_start
            date_end = data.date_end
            partner_id = data.partner_id.id
            brand_id = data.brand_id.id
            
        
        return {
            'name': _('Partner Statement'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'view_id': template_id,
            'domain': [('type','in',('out_invoice','in_invoice')),('partner_id','=',partner_id),('brand_id','=',brand_id),('date_invoice','>=',date_start),('date_invoice','<=',date_end)],
            
        }
