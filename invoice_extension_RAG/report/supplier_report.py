from openerp.report import report_sxw
from datetime import datetime
import openerp.tools

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
        })

#report_sxw.report_sxw('supplier_aeroo_report_xls', 'account.invoice', 'invoice_extension_RAG/report/', parser=order, header=True)

