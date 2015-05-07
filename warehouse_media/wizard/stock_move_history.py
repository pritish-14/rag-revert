
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

class wizard_move_history(osv.osv):

    _name = 'wizard.move.history'
    _description = 'Wizard that print the stock move history'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),        
    }

    _defaults = {
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        return self.pool['report'].get_action(
            cr, uid, [],
            'warehouse_media.report_stockmove',
            data=data, context=context)

class wiz_stock_valuation(osv.osv):

    _name = 'wiz.stock.valuation'
    _description = 'Wizard that print the stock valuation'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),        
    }

    _defaults = {
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        return self.pool['report'].get_action(
            cr, uid, [],
            'warehouse_media.report_stockvaluation',
            data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
