from openerp.osv import osv, fields
from datetime import datetime

class news(osv.osv):
    _name = "news"
    _columns = {
        'news_time':fields.many2one('news.times', 'News Times'),
        'news_headline': fields.char('News Headline'),
        'station_ids': fields.many2one('brand',"Station", required='True' ),
        'user_id': fields.many2one('res.users', 'Submitted by'),
        'creation_date':fields.datetime('Creation Date'),
    }
    
    _defaults = {
        'creation_date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cursor, user, context: user,
    }
	
'''class brand(osv.osv):
	_name = 'brand'
	_columns = {
		'name': fields.char("Name", required='True'),
		'type': fields.selection([('1', "Radio"), ('2', 'TV'), ('3', 'Digital')],
		                         "Type", required='True'),
		'company_id': fields.many2one('res.company', 'Company', required=True, select=1),
		
	}  ''' 
    
