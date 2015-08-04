from openerp.osv import osv, fields

class account_common_report(osv.osv_memory):
    _inherit = 'account.report.general.ledger'
    
    _columns = {
        'account_ids': fields.many2many('account.account', 'account_report_general_ledger_account_rel', 'account_id', 'id1', 'Accounts'),
#         'account_ids' : fields.many2many('account.account', 'report_account_rel', 'account_id', 'rel_id', 'Accounts'),
        'display_account': fields.selection([('all','All'), ('movement','With movements'),
                                            ('not_zero','With balance is not equal to 0'),
                                            ('none', 'Selected Accounts')
                                            ],'Display Accounts', required=True),
    }
    
    _defaults = {
        'journal_ids' : []
    }
account_common_report()

class account_partner_balance(osv.osv_memory):
    """
        This wizard will provide the partner balance report by periods, between any two dates.
    """
    _inherit = 'account.partner.balance'
    
    _columns = {
        'account_ids': fields.many2many('account.account', 'account_partner_balance_rel_ifrs', 'account_id', 'id4', 'Accounts'),
    }
    
    _defaults = {
        'journal_ids' : []
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        acc_ids = self.browse(cr, uid, ids[0], context=context).account_ids
        accounts = [acc.id for acc in acc_ids]
        data['form'].update({'account_ids' : accounts})
        data['form'].update(self.read(cr, uid, ids, ['display_partner'])[0])
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.partner.balance1',
            'datas': data,
    }

account_partner_balance()

class account_balance_report(osv.osv_memory):
    _inherit = "account.common.account.report"

    _columns = {
        'account_ids': fields.many2many('account.account', 'account_central_journal_account_rel_ifrs', 'account_id', 'id3', 'Accounts'),
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance', 'datas': data}

account_balance_report()


class account_print_journal(osv.osv_memory):
    
    _inherit = 'account.print.journal'
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        acc_ids = self.browse(cr, uid, ids[0], context=context).account_ids
        accounts = [acc.id for acc in acc_ids]
        data['form'].update({'account_ids' : accounts})
        data['form'].update(self.read(cr, uid, ids, ['sort_selection'], context=context)[0])
        if context.get('sale_purchase_only'):
            report_name = 'account.journal.period.print.sale.purchase1'
        else:
            report_name = 'account.journal.period.print1'
        return {'type': 'ir.actions.report.xml', 'report_name': report_name, 'datas': data}
    
    _columns = {
        'account_ids': fields.many2many('account.account', 'account_sales_purchase_journal_account_rel', 'account_id', 'id2', 'Accounts'),
    }
    
account_print_journal()

class account_central_journal(osv.osv_memory):
    
    _inherit = 'account.central.journal'
    
    _columns = {
        'account_ids': fields.many2many('account.account', 'account_central_journal_account_rel_ifrs', 'account_id', 'id3', 'Accounts'),
    }
    
    _defaults = {
        'journal_ids' : []
    }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        acc_ids = self.browse(cr, uid, ids[0], context=context).account_ids
        accounts = [acc.id for acc in acc_ids]
        data['form'].update({'account_ids' : accounts})
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.central.journal1',
                'datas': data,
        }

account_central_journal()

class account_partner_ledger(osv.osv_memory):
    
    _inherit = 'account.partner.ledger'
    
    _columns = {
        'account_ids': fields.many2many('account.account', 'account_partner_ledger_rel_ifrs', 'account_id', 'id4', 'Accounts'),
    }
    
    _defaults = {
        'journal_ids' : []
    }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['initial_balance', 'filter', 'page_split', 'amount_currency'])[0])
        acc_ids = self.browse(cr, uid, ids[0], context=context).account_ids
        accounts = [acc.id for acc in acc_ids]
        data['form'].update({'account_ids' : accounts})
        if data['form']['page_split']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.third_party_ledger1',
                'datas': data,
        }
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.third_party_ledger_other1',
                'datas': data,
        }
    
account_partner_ledger()
