from openerp.osv import osv, fields

class account_partner_ledger(osv.osv_memory):
    
    _inherit = 'account.partner.ledger'
    
    def check_report_aeroo(self, cr, uid, ids, context=None):
        data = super(account_partner_ledger, self).check_report(cr, uid, ids, context=context)['datas']
        return { 'type': 'ir.actions.report.xml', 'report_name': 'partner_ledger_aeroo_report', 'datas': data}

class account_print_journal(osv.osv_memory):
    
    _inherit = 'account.print.journal'
    
    def check_report_aeroo(self, cr, uid, ids, context=None):
        data = super(account_print_journal, self).check_report(cr, uid, ids, context=context)['datas']
        if context.get('sale_purchase_only'):
            report_name = 'iel_sales_purchase_journal_aeroo_report'
        else:
            report_name = 'iel_journal_aeroo_report'
        return { 'type': 'ir.actions.report.xml', 'report_name': report_name, 'datas': data}


class account_general_journal(osv.osv_memory):
    
    _inherit = 'account.general.journal'
    
    def check_report_aeroo(self, cr, uid, ids, context=None):
        data = super(account_general_journal, self).check_report(cr, uid, ids, context=context)['datas']
        return { 'type': 'ir.actions.report.xml', 'report_name': 'iel_general_journal_aeroo_report', 'datas': data}

class account_central_journal(osv.osv_memory):
    
    _inherit = 'account.central.journal'
    
    def check_report_aeroo(self, cr, uid, ids, context=None):
        data = super(account_central_journal, self).check_report(cr, uid, ids, context=context)['datas']
        return { 'type': 'ir.actions.report.xml', 'report_name': 'iel_central_journal_aeroo_report', 'datas': data}
    
class account_partner_balance(osv.osv_memory):
    
    _inherit = 'account.partner.balance'
    
    def check_report_aeroo(self, cr, uid, ids, context=None):
        data = super(account_partner_balance, self).check_report(cr, uid, ids, context=context)['datas']
        return { 'type': 'ir.actions.report.xml', 'report_name': 'iel_partner_balance_aeroo_report', 'datas': data}
  
class account_analytic_journal_report(osv.osv_memory):
    _inherit = 'account.analytic.journal.report'
      
    def check_report_aeroo(self, cr, uid, ids, context=None):
        data = self.check_report(cr, uid, ids, context=context)['datas']
        return { 'type': 'ir.actions.report.xml', 'report_name': 'iel_analytic_journal_aeroo_report', 'datas': data}

