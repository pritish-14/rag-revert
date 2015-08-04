from openerp.tools import config
from openerp.tools.translate import _
from openerp.osv import osv
from operator import itemgetter
from openerp.addons.account.report.account_general_journal import journal_print

class Parser(journal_print):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
