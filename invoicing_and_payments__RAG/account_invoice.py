import time
from openerp.osv import fields, osv

class account_invoice(osv.osv):

    _inherit = "account.invoice"
    _description = 'Invoice'

    def _get_default_section_id(self, cr, uid, context=None):
        """ Gives default section by checking if present in the context """
        return self._resolve_section_id_from_context(cr, uid, context=context) or False

    def _resolve_section_id_from_context(self, cr, uid, context=None):
        """ Returns ID of section based on the value of 'section_id'
            context key, or None if it cannot be resolved to a single
            Sales Team.
        """
        if context is None:
            context = {}
        if type(context.get('default_section_id')) in (int, long):
            return context.get('default_section_id')
        if isinstance(context.get('default_section_id'), basestring):
            section_name = context['default_section_id']
            section_ids = self.pool.get('crm.case.section').name_search(cr, uid, name=section_name, context=context)
            if len(section_ids) == 1:
                return int(section_ids[0][0])
        return None


    _columns = {
        'brand_id': fields.many2one('brand', 'Brand'),
        'section_ids': fields.many2one('crm.case.section', 'Sales Team'),
        'industry_id': fields.many2one('partner.industry',"Industry"),
    }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'section_ids': lambda s, cr, uid, c: s._get_default_section_id(cr, uid, c),
    }

    def on_change_user(self, cr, uid, ids, user_id, context=None):
        """ When changing the user, also set a section_id or restrict section id
            to the ones user_id is member of. """
        if user_id:
            section_ids = self.pool.get('crm.case.section').search(cr, uid, ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)], context=context)
            if section_ids:
                return {'value': {'section_id': section_ids[0]}}
        return {'value': {}}

class account_invoice(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
        'brand_ids': fields.related('invoice_id', 'brand_id', type="many2one", relation="brand", string="Brand"),
    }

class brand(osv.osv):
    _name = 'brand'
    _columns = {
        'name': fields.char("Name"),
        'type': fields.selection([('1', "Radio"), ('2', 'TV'), ('3', 'Digital')],
                                 "Type", required='True'),
        
    }

class account_invoice(osv.osv):
    _inherit = "account.voucher"

    def print_supplier_report(self, cr, uid, ids, context=None):
        if context is None:
            context= {}

        datas = {
             'ids': ids,
             'model': 'account.voucher',
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'supplier_aeroo_report_xls',
            'datas': datas,
        }

