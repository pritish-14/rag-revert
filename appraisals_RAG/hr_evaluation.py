from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

class hr_evaluation(osv.Model):
    _inherit = "hr_evaluation.evaluation"

    def print_report_evaluation(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        contract_obj = self.pool.get('hr_evaluation.evaluation')
        data = self.read(cr, uid, ids, context=context)[0]
        contract_ids = contract_obj.search(cr, uid, [], context=context) or []
        datas = {
             'ids': contract_ids,
             'model': 'hr_evaluation.evaluation',
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'appraisal_aeroo_report_doc',
            'datas': datas,
        }


