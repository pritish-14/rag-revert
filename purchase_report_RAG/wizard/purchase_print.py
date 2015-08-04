from datetime import date, timedelta
import time
from openerp.osv import osv, fields
from openerp.tools.translate import _

class purchase_print(osv.osv):
    _name = "purchase.print"

    _columns = {
        'company_id':fields.many2one('res.company', 'Company', required=True),
    }
    
    _defaults = {
            'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.print',context=c),
    }

    def print_report(self, cr, uid, ids, context=None):
#        assert len(ids) == 1
        contract_obj = self.pool.get('purchase.report')        
        data = self.read(
            cr, uid, ids, ["company_id"], context)[0]
        contract_ids = contract_obj.search(cr, uid, [('id', '!=', False)], context=context) or []            
        datas = {
             'ids': contract_ids,
             'model': 'purchase.report',
             'form': data
        }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'purchase_aeroo_report_xls',
                'datas': datas}
                
    def print_report_purchase(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ir_model_data = self.pool.get('ir.model.data')
        template_id = ir_model_data.get_object_reference(cr, uid, 'purchase_report_RAG', 'view_purchase_statistics_tree')[1]            
        
        return {
            'name': _('Purchase Statistics'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'purchase.report',
            'type': 'ir.actions.act_window',
            'view_id': template_id,
        }

