from openerp.osv import osv, fields
from datetime import datetime, timedelta
import datetime
from datetime import date

class daily_traffic(osv.osv):
    _name = "daily.traffic"
    #_rec_name = 'std_id'

    _columns = {
    'state': fields.selection([
            ('draft','Draft'),
            ('scheduled','Scheduled'),
            ('executed','Executed'),
            ('cancelled','Cancelled'),
            ], 'Status', readonly=True),
    'ref': fields.char('Reference'),
    'brand_id': fields.many2one('brand','Brand',required=1),
    'create_date': fields.datetime('Creation Date',readonly=1),
    'traffic_date': fields.date('Traffic Date',required=1),
    'responsible': fields.many2one('res.users','Responsible',required=1),
    'company_id': fields.many2one('res.company', 'Company', required=False),
    'traffic_line': fields.one2many('daily.traffic.lines', 'traffic_id', 'Traffic Lines'),
    }
    _defaults = {
    	'create_date': fields.date.context_today,
    	'traffic_date': fields.date.context_today,
        'state': 'draft',
    	'responsible': lambda obj, cr, uid, context: uid,
    	'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'daily.traffic', context=c),
    	#self.write(cr, uid, ids,{'ref': self.pool.get('ir.sequence').get(cr, uid, 'daily.traffic')or '/'},context=context)
    }
    
    def traffic_scheduled(self, cr, uid, ids, context=None):
     	self.write(cr, uid, ids, {'state' : 'scheduled','ref': self.pool.get('ir.sequence').get(cr, uid, 'daily.traffic')or '/'})
     	return True
     	
    def traffic_executed(self, cr, uid, ids, context=None):
     	self.write(cr, uid, ids, {'state' : 'executed'})
     	return True
     	
    def traffic_cancel(self, cr, uid, ids, context=None):
     	self.write(cr, uid, ids, {'state' : 'cancelled'})
     	return True
    	
class daily_traffic_lines(osv.osv):
    _name = "daily.traffic.lines"

    _columns = {
    'traffic_id': fields.many2one('daily.traffic','Line ID'),
    'status': fields.selection([
            ('draft','Draft'),
            ('scheduled','Scheduled'),
            ('executed','Executed'),
            ('notexe','Not Executed'),
            ], 'Status'),
    'spot_id': fields.char('Spot ID'),
    'time_start': fields.datetime('Time Start'),
    'time_end': fields.datetime('Time End'),
    'product': fields.many2one('product.product','Product'),
    'description': fields.char('Description'),
    'cart': fields.integer('Cart No.'),
    'advertiser': fields.many2one('res.partner','Advertiser'),
    'remark': fields.char('Remarks'),
    }
    

