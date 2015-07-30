from datetime import date, timedelta
import time
from openerp.osv import osv, fields

class hr_applicant(osv.Model):
    _inherit = "hr.applicant"

    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),        
    }
    
    _defaults = {
            'fiscalyear_id': _get_fiscalyear,
    }

    def print_report_recruitment(self, cr, uid, ids, context=None):
        if context is None:
            context= {}
        
        contract_obj = self.pool.get('hr.applicant')
        data = self.read(cr, uid, ids, context=context)[0]
        contract_ids = contract_obj.search(cr, uid, [], context=context) or []
        datas = {
             'ids': contract_ids,
             'model': 'hr.applicant',
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'interview_aeroo_report_doc',
            'datas': datas,
        }


class recruitment_print(osv.Model):
    _name = "recruitment.print"

    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    _columns = {
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),        
    }
    
    _defaults = {
            'fiscalyear_id': _get_fiscalyear,
            'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.common.report',context=c),
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
