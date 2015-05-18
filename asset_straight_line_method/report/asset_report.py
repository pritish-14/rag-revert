from openerp.report import report_sxw
from datetime import datetime
import openerp.tools

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({})
        

