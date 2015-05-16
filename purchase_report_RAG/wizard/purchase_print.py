from datetime import date, timedelta
import time
from openerp.osv import osv, fields

class purchase_print(osv.osv):
    _name = "purchase.print"

    _columns = {
        'company_id':fields.many2one('res.company', 'Company', required=True),
    }
    
    _defaults = {
            'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.print',context=c),
    }

    def print_report(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        contract_obj = self.pool.get('purchase.report')        
        data = self.read(
            cr, uid, ids, ["company_id"], context)[0]
        contract_ids = contract_obj.search(cr, uid, [], context=context) or []            
        datas = {
             'ids': contract_ids,
             'model': 'purchase.report',
             'form': data
        }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'purchase_aeroo_report_xls',
                'datas': datas}
