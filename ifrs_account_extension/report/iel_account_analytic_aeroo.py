from openerp.tools import config
from openerp.tools.translate import _
from openerp.osv import osv
from operator import itemgetter
from analytic_journal_ifrs import account_analytic_journal

class Parser(account_analytic_journal):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_object_name' : self.get_object_name,
            'get_object_code' : self.get_object_code
        })
        
    def get_object_name(self, id):
        analytic_obj = self.pool.get("account.analytic.journal")
        if id:
            analytic_data = analytic_obj.browse(self.cr, self.uid, id)
            return analytic_data.name
        
    def get_object_code(self, id):
        analytic_obj = self.pool.get("account.analytic.journal")
        if id:
            analytic_data = analytic_obj.browse(self.cr, self.uid, id)
            return analytic_data.code
            
