# -*- coding: utf-8 -*-
##############################################################################
import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler

class issue_voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(issue_voucher, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc':self.get_product_desc
        })
    def get_product_desc(self,move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc

report_sxw.report_sxw('report.issue.voucher.print','issue.order','addons_aug/material_issue_register/report/issue_voucher.rml',parser=issue_voucher)
report_sxw.report_sxw('report.waybill','issue.order','addons_aug/material_issue_register/report/waybill.rml',parser=issue_voucher)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

