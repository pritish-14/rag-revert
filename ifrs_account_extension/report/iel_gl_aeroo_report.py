from openerp.tools import config
from openerp.tools.translate import _
from openerp.osv import osv
from operator import itemgetter
from report_general_ledger import account_general_ledger

class Parser(account_general_ledger):
    
    def __init__(self, cr, uid, name, context):
        
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_display_account' : self.get_display_account,
            'set_data' : self.set_data,
        
        })
    
    def get_display_account(self, display_account):
        
        if display_account == 'all' :
            return 'All'
        elif display_account == 'movement' :
            return 'With movements'
        elif display_account == 'none':
            return 'Selected Accounts'
        else:
            return 'With balance is not equal to 0'
        
    def set_data(self, indent):
        new_name = ""
        if indent:
            for i in range(0,indent):
                new_name += " "
        return new_name
