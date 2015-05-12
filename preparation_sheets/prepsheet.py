from openerp.osv import osv, fields
import datetime
from datetime import datetime

class sheet(osv.osv):
    _name = "sheet"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
        #'table_ids': fields.one2many('content.table', 'table_id', 'Content Table'),
        'sheet_no':fields.char('Prep Sheet No'),
        'date':fields.datetime('Date'),
        'show':fields.many2one('show.entry','Show'),
        'user_id': fields.many2one('res.users', 'Presenter'),
        'brand_id': fields.many2one('brand', 'Station', required=1),
        'creation_date': fields.datetime('Creation Date'),
        'day': fields.char('Day'),
        'earlier_week': fields.text('Earlier This Week', width = 40, height=2),
        'later_week': fields.text('Coming Up Later This Week'),
        'next_week': fields.text('Coming Up Next Week'),
        'miss_today': fields.text('What did we miss today that can be used tomorrow?'),
        'major_bit': fields.text('Major Bit'),
        'minor_bit': fields.text('Minor Bit'),
        'filler_1': fields.text('Filler 1'),
        'filler_2': fields.text('Filler 2'),
        'phone_topic': fields.text('Phone Topic'),
        'notes_h1': fields.text('NOTES'),
        'major_h2': fields.text('Major Bit'),
        'minor_h2': fields.text('Minor Bit'),
        'filler_1h2': fields.text('Filler 1'),
        'filler_2h2': fields.text('Filler 2'),
        'phone_h2': fields.text('Phone Topic'),
        'notes_h2': fields.text('NOTES'),
        'major_h3': fields.text('Major Bit'),
        'minor_h3': fields.text('Minor Bit'),
        'filler_1h3': fields.text('Filler 1'),
        'filler_2h3': fields.text('Filler 2'),
        'phone_h3': fields.text('Phone Topic'),
        'notes_h3': fields.text('NOTES'),
        'major_h4': fields.text('Major Bit'),
        'minor_h4': fields.text('Minor Bit'),
        'filler_1h4': fields.text('Filler 1'),
        'filler_2h4': fields.text('Filler 2'),
        'phone_h4': fields.text('Phone Topic'),
        'notes_h4': fields.text('NOTES'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ], 'Status', readonly=True),
        'notes': fields.text('Notes', states={'draft': [('readonly', False)]}),     
    }
    
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        #'date': fields.date.context_today,
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'creation_date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'day': datetime.now().strftime("%A"),
        'state': 'draft'
    }

    def submit_confirm(self, cr, uid, ids, context=None):
        seq = self.pool.get('ir.sequence').get(cr, uid, 'sheet') or '/'
        self.write(cr, uid, ids, {'state': 'confirmed', 'sheet_no': seq})
        return True

    def submit_reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
        
        
'''class content_table(osv.osv):
    _name = "content.table"
    _columns = {
        'table_id': fields.many2one('sheet', 'Content Table Id'),
        'event':fields.char('Event'),
        'date_time':fields.datetime('Time'),
        'content':fields.char('Content/Prep'),
    }

    _defaults = {
        'date_time': fields.date.context_today,
    }'''

