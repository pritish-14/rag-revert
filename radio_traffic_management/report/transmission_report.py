import time
from openerp.report import report_sxw


class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.traffic.transmission.report', 'report_daily_traffic', 'radio_traffic_management/report/transmission_report.rml', parser=order, header=False)
