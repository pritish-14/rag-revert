from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.report import report_sxw

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _columns = {
        'description': fields.char('Description', size=64),
    }
    
# class account_move(osv.osv):
#     _inherit = "account.move"
#     def button_validate(self, cr, uid, ids, context=None):
#         for move in self.browse(cr, uid, ids, context=context):
#             for line in move.line_id:
#                 if not line.description:
#                     raise osv.except_osv(_('Warning!'),
#                                          _('Please fill Description in journal Items before validating Journal Entry.'))
#         return super(account_move, self).button_validate(cr, uid, ids, context=context)