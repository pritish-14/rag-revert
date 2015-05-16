# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
import xlwt

class excel_asset_register_report(osv.TransientModel):
    _name = "excel.asset.register.report"
    
    def _get_export_data(self, cr, uid, context=None):
        if context is None:
            context = {}
        asset_register_obj = self.pool.get('account.asset.asset')
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 280')
        row = 0
        style = xlwt.easyxf('align: wrap no')
        style1 = xlwt.easyxf('align: wrap no, vert center, horiz right;')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 5000
        worksheet.col(7).width = 5000
        worksheet.col(8).width = 5000
        worksheet.col(9).width = 5000
        worksheet.row(0).height = 500
        worksheet.write(row, 0, 'Purchase Date' ,header)
        worksheet.write(row, 1, 'Reference', header)
        worksheet.write(row, 2, 'Asset Name', header)
        worksheet.write(row, 3, 'Asset Category', header)
        worksheet.write(row, 4, 'Gross Value', header)
        worksheet.write(row, 5, 'Salvage Value', header)
        worksheet.write(row, 6, 'Residual Value', header)
        worksheet.write(row, 7, 'Depreciation in Period', header)
        worksheet.write(row, 8, 'Total Depreciation', header)
        worksheet.write(row, 9, 'Current Value', header)        
        row += 1
        for asset in asset_register_obj.browse(cr, uid, context):
            worksheet.write(row, 0, tools.ustr(asset.purchase_date) ,style)
            worksheet.write(row, 1, tools.ustr(asset.code) ,style)
            worksheet.write(row, 2, tools.ustr(asset.name) ,style)
            worksheet.write(row, 3, tools.ustr(asset.category_id) ,style)
            worksheet.write(row, 4, tools.ustr(asset.purchase_value) ,style)
            worksheet.write(row, 5, tools.ustr(asset.salvage_value) ,style)
            worksheet.write(row, 6, tools.ustr(asset.value_residual) ,style)
#                worksheet.write(row, 7, '%.2f' ,style)
#               worksheet.write(row, 8, '%.2f' ,style)
#              worksheet.write(row, 9, '%.2f' ,style)
        row += 1
        borders = xlwt.Borders()
        borders.top = xlwt.Borders.MEDIUM
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle() # Create Style
        border_style.borders = borders
        
        file = StringIO()
        workbook.save(file)
        file.seek(0)
        record = file.read()
        file.close()
        return base64.b64encode(record)

    _columns = {
        'file':fields.binary("Save As"),
        'name':fields.char("Name", size=32, readonly=True, invisible=True)
    }

    _defaults = {
        'name':"Asset_Summary.xls",
        'file': _get_export_data
    }


class asset_register_wiz(osv.osv):
    _name = 'asset.register.wiz'

    _columns = {
                'company_id': fields.many2one('res.company', 'Company', readonly="1"),                
                'start_date': fields.date('Start Date'),
                'end_date': fields.date('End Date'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'asset.register.wiz', context=c),
        }    

    def export_asset_report(self, cr, uid, ids, context):
        data = self.read(cr, uid, ids)[0]
        context.update({'start_date': data['start_date'], 'end_date': data['end_date']})
        return {
              'name': _('Binary'),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'excel.asset.register.report',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context,
        }
        
    def print_report_new(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        asset_obj = self.pool.get('account.asset.asset')
        data = self.read(cr, uid, ids, context=context)[0]
        print "start_date", data.start_date
        asset_ids = asset_obj.search(cr, uid, [('purchase_date','&gt;=',data.start_date)('purchase_date','&lt;=',data.end_date)], context=context) or []
        print "asset_idsasset_idsasset_ids", asset_ids
        datas = {
             'ids': asset_ids,
             'model': 'account.asset.asset',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'asset_aeroo_report_xls',
            'datas': datas,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
