# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import fields, osv

class report_bank_balance(osv.osv_memory):
    _inherit = "account.common.account.report"
    _name = 'report.bank.balance'

    _columns = {
        'journal_ids': fields.many2many('account.journal', 'bank_balance_report_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
        'sortby': fields.selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], 'Sort by'),
    }

    _defaults = {
        'journal_ids': [],
        'display_account': 'all',
        'target_move': 'all',
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml', 'report_name': 'bank.balance.list', 'datas': data}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
