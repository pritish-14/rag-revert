from openerp.osv import osv, fields
from datetime import date,datetime

class script(osv.osv):
    _name = "script"
    _inherit = ['mail.thread', 'ir.needaction_mixin','pad.common']
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
        ('pending', 'Pending'),
    ]

    _track = {

        'state': {
            'script_management.script_awaiting_approval': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'awaiting_approval',
            'script_management.script_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
            'script_management.script_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
            'script_management.script_pending': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'pending',

        },
    }

    _columns = {
        'script_pad': fields.char('Script', pad_content_field='notes'),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'advertiser_id': fields.many2one('res.partner', 'Advertiser'),
        'writer_id': fields.many2one('res.users', 'Writer'),
        'script_no':fields.char('Script No.'),
        'date':fields.datetime('Assigned Date', readonly=1),
        'user_id': fields.many2one('res.users', 'Sales Executive'),
        'brand_id': fields.many2one('brand', 'Brand'),
        'state': fields.selection(STATE_SELECTION,
            'Status', readonly=True, select=True),
        'notes': fields.text('Notes', states={'draft': [('readonly', False)]}),
        'script_name': fields.char("Script Name", required="1"),
        'c_date': fields.date('Completion Date', readonly=1),
        'approved_by': fields.many2one('res.users', 'Approved By', readonly=1),
        
         
        #'manager_id': fields.many2one('res.users', 'Manager', select=True, track_visibility='onchange', readonly=1),    
    }
    
    _defaults = {
        #'user_id': lambda obj, cr, uid, context: uid,
        'writer_id': lambda obj, cr, uid, context: uid,
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft'
    }
    
   # def on_change_user(self, cr, uid, ids, user_id, context=None):
      #  """ When changing the user, also set a section_id or restrict section id
       #     to the ones user_id is member of. """
#        section_id = self._get_default_section_id(cr, uid, user_id=user_id, context=context) or False
       # if user_id and self.pool['res.users'].has_group(cr, uid, 'base.group_multi_salesteams'):
          #  section_ids = self.pool.get('crm.case.section').search(cr, uid, ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)], context=context)
           # if section_ids:
              #  section_id = section_ids[0]
              #  manager_id = self.pool.get('crm.case.section').browse(cr, uid, section_id).user_id                            
                #return {'value': {'section_id': section_id, 'manager_id': manager_id.id}}

    def submit_approval(self, cr, uid, ids, context=None):
        seq = self.pool.get('ir.sequence').get(cr, uid, 'script') or '/'
        self.write(cr, uid, ids, {'state': 'awaiting_approval', 'script_no': seq, 'c_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        return True
        
    def approve_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved'})#, 'approved_by': lambda obj, cr, uid, context: uid})
        return True

    def cancel_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def pending_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'pending'})
        return True

    def reset_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True    

