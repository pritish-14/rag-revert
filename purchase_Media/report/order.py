import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.purchase.order5','purchase.order','purchase_Media/report/order.rml',parser=order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

