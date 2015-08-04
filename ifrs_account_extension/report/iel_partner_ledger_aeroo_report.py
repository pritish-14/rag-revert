from openerp.tools import config
from openerp.tools.translate import _
from openerp.osv import osv
from operator import itemgetter
from account_partner_ledger_ifrs import third_party_ledger

class Parser(third_party_ledger):
    
    def __init__(self, cr, uid, name, context):
        
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_partner' : self.get_partner
        })
        
    def get_partner(self, partner):
        
        if partner == 'customer':
            return 'Receivable Accounts'
        elif partner == 'supplier':
            return 'Payable Accounts'
        else:
            return 'Receivable and Payable Accounts'
