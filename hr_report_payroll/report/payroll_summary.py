import time
from openerp.report import report_sxw


class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.payroll.summary.report', 'report_payroll_summary', 'hr_report_payroll/report/payroll_summary.rml', parser=order, header=False)
