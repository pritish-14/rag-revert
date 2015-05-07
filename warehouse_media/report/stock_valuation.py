from datetime import datetime
from openerp.osv.fields import datetime as datetime_field
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.osv import orm
import logging
#from common_report_header import common_report_header


class prep_stock_valuation(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(prep_stock_valuation, self).__init__(
            cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            })


                
class stock_valuation(orm.AbstractModel):
    _name = 'report.warehouse_media.report_stockvaluation'
    _inherit = 'report.abstract_report'
    _template = 'warehouse_media.report_stockvaluation'
    _wrapped_report_class = prep_stock_valuation

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
