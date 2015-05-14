from datetime import date, timedelta

from openerp.osv import osv, fields


class recruitment_print(osv.Model):
    _name = "recruitment.print"

    _columns = {
        'company_id':fields.many2one('res.company', 'Company', required=True),
    }

    def print_report(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        data = self.read(
            cr, uid, ids, ["company_id"], context)[0]
        datas = {
             'ids': ids,
             'model': 'hr.applicant',
             'form': data
        }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'recruitment_aeroo_report_xls',
                'datas': datas}
