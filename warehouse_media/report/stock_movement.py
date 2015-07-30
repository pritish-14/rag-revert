from datetime import datetime
from openerp.osv.fields import datetime as datetime_field
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.osv import orm
import logging
#from common_report_header import common_report_header


class partner_open_arap_print(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(partner_open_arap_print, self).__init__(
            cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            })


                
class wrapped_vat_declaration_print(orm.AbstractModel):
    _name = 'report.warehouse_media.report_stockmove'
    _inherit = 'report.abstract_report'
    _template = 'warehouse_media.report_stockmove'
    _wrapped_report_class = partner_open_arap_print

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
