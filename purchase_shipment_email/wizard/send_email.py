from datetime import datetime, timedelta
import time
import datetime
from openerp.osv import osv, fields

class SendEmail(osv.osv_memory):
    _name = 'send.email'
    
    def send(self, cr, uid, ids, context=None):
        
        date = datetime.datetime.now().date()
        
        #print "Date == > ", str(date)
        #print type(date)
        stock_obj = self.pool.get('stock.picking')
        p_id =stock_obj.search(cr, uid,
            [('state', 'not in', ['cancel','done']),('min_date','<', str(date))], context=context)
            
        print p_id
       
        stock_rcrds = stock_obj.browse(cr, uid, p_id, context=context) 
        print stock_rcrds
        for stock in stock_rcrds:
              print stock.origin 
        
        
        return True
