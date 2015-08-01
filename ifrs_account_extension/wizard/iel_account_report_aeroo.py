from openerp.osv import osv, fields

class account_report_general_ledger(osv.osv_memory):
    
    _inherit = 'account.report.general.ledger'
    
    def check_report_aeroo(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = super(account_report_general_ledger, self).check_report(cr, uid, ids, context=context)
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move', 'display_account'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        
        return { 'type': 'ir.actions.report.xml', 'report_name': 'account_general_ledger_aeroo_report', 'datas': data}
    
class account_balance_report(osv.osv_memory):
    
    _inherit = 'account.balance.report'
    
    def check_report_aeroo(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = super(account_balance_report, self).check_report(cr, uid, ids, context=context)
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids','account_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move', 'display_account'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return { 'type': 'ir.actions.report.xml', 'report_name': 'account_trial_balance_aeroo_report', 'datas': data}
    
class account_partner_balance(osv.osv_memory):
    """
        This wizard will provide the partner balance report by periods, between any two dates.
    """
    _inherit = 'account.partner.balance'
    
    def check_report_aeroo(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = super(account_partner_balance, self).check_report(cr, uid, ids, context=context)
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids','account_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move', 'display_account'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.partner.balance1',
            'datas': data,
    }
        
