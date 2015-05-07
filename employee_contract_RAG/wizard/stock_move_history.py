
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

class wizard_move_history(osv.osv_memory):

    _name = 'wizard.move.history'
    _description = 'Wizard that print the stock move history'
    _columns = {
        'choose_date': fields.boolean('Choose a Particular Date'),
        'date': fields.datetime('Date', required=True),
    }

    _defaults = {
        'choose_date': False,
        'date': fields.datetime.now,
    }

    def open_table(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        ctx = context.copy()
        ctx['history_date'] = data['date']
        ctx['search_default_group_by_product'] = True
        ctx['search_default_group_by_location'] = True
        return {
            'domain': "[('date', '<=', '" + data['date'] + "')]",
            'name': _('Stock Value At Date'),
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'stock.history',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }



