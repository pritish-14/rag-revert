from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
from datetime import datetime,date
from json import dumps
import time
import datetime

class Joining(osv.osv):
	_name = 'joining'
	_description = 'Employee Joining'
	_inherit = 'mail.thread'
    
	def _current_employee_get(self, cr, uid, context=None):
		ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
		if ids:
			return ids[0]
		return False

	_columns = {
		'state': fields.selection([('in_progress',"In Progress"),
        									  ('w_c_a', "Awaiting CEO Approval"),('induction', "Induction"),('closed',"Closed")],"Status"),
		'employee_id':fields.many2one('hr.employee','Employee',required=True),
		'job_Position':fields.many2one('hr.job','Job Position',required=True),
		'department_id':fields.many2one('hr.department','Department',required=True),
		'joining_date':fields.datetime('Joining Date',required=True, readonly=True),
		'required_items':fields.one2many('req.items','req_id','Required Items'),
		'confirm_receipt':fields.boolean('Confirmation Receipt'),
		's_w_email':fields.boolean('Send Welcome Email'),
		'i_to_staff':fields.boolean('Introduction to Staff'),
		's_id_card':fields.boolean('Submit ID Card Form'),
		's_m_form':fields.boolean('Submit Medical Form'),
		'induction':fields.one2many('induction','ind_id','Induction'),
		'emp_joining_ref':fields.char('Employee Joining Reference'),
	}
	_defaults = {
		'joining_date': datetime.datetime.now(),
        #'state': 'in_progress',
        'employee_id': _current_employee_get,
	    }
	    
	    
	_track = {
		'state': {
			'employee_joining.mt_alert_request_joining_progress': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'in_progress',
			'employee_joining.mt_alert_request_joining_ceo_approval': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'w_c_a',
			'employee_joining.mt_alert_request_joning_induction': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'induction',
			'employee_joining.mt_alert_request_joning_closed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'closed',
		},
	}
	
	def onchange_joiningdate(self, cr, uid, ids, employee_id, context=None):
		print "AAAAAAAAAAAAAAAAAA"
		if not employee_id:
			return {'value': {'job_id': False}}
		emp_obj = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
		if emp_obj.job_id:
			job_id = emp_obj.job_id.id
		else:
			raise osv.except_osv(_("Fill all mandatory fields of empolyee first."),'')
		print "JJJJJJJJJJJJJJJJJJJJJJJJJ", job_id
		return {'value': {'job_Position': job_id}}
	
	def onchange_employee_id(self,cr, uid, ids, employee_id, context=None):
		emp_read = self.pool.get('hr.employee').browse(cr, uid, employee_id)        
		res = {
			'department_id':emp_read.department_id,
			'job_Position':emp_read.job_id,
		}        
		return {'value':res}    
	
	def create(self, cr, uid, vals, context=None):
		if vals.get('emp_joining_ref','/')=='/':
			vals['emp_joining_ref'] = self.pool.get('ir.sequence').get(cr, uid, 'joining') or '/'
			return super(Joining, self).create(cr, uid, vals, context=context)
    
	def copy(self, cr, uid, id, default=None, context=None):
		print "Hi---------------------------"
		if not default:
			default = {}
		default.update({
			'state': 'in_progress',
			'emp_joining_ref': self.pool.get('ir.sequence').get(cr, uid, 'medical.premium'),
})    
	
	'''def state_in_progress(self, cr, uid, ids, context=None):
		print"--------------two"
		self.write(cr,uid, ids, {'state':'in_progress'}, context=context)
		#self.write(cr, uid, ids, {'emp_joining_ref':self.pool.get('ir.sequence').get(cr, uid, 'joining') or '/'},context=context)
		return True
	
	def state_coo_aproval(self,cr,uid, ids, context=None):
		print"--------------three"
		self.write(cr,uid, ids, {'state':'w_c_a'}, context=context)
		return True
	
	def state_induction(self, cr, uid, ids, context=None):
		print"--------------four"
		self.write(cr, uid, ids, {'state': 'induction'}, context=context)
		return True

	def state_reset(self, cr, uid, ids, context=None):
		print"--------------five"
		self.write(cr, uid, ids, {'state': 'in_progress'}, context=context)

	def state_close(self, cr, uid, ids, context=None):
		print"--------------six"
		self.write(cr, uid, ids, {'state': 'closed'}, context=context)
		return True'''
		
	def mymod_inprogress(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state' : 'in_progress' })
		return True

	def mymod_aproval(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state' : 'w_c_a' })
		return True

	def mymod_induction(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state' : 'induction' })
		return True

	def mymod_close(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state' : 'closed' })
		return True
		

	'''def mymod_lost(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state' : 'lost' })
		return True'''
		
			 	 

    
class Required_Items(osv.osv):
	_name = 'req.items'
	_rec_name='item_name'
	
	_columns = {
	
		'req_id': fields.many2one('joining',"Required Item"),
		'item_name'	: fields.char('Item Name', required=True),
		'quantity': fields.float('Quantity', required=True),
		'department_id':fields.many2one('hr.department','Department',required=True),
		'remarks': fields.char("Remarks", required=True),
		'status': fields.selection([('in_progress',"In Progress"),
        									  ('received', "Received")],"Status",required=True),
		'status1': fields.selection([('in_progress',"In Progress"),
        									  ('received', "Received")],"Status"),
		}
		
	_defaults = {
		'status': 'in_progress',
        #'state': 'in_progress',
        #'employee_id': lambda self, cr, uid, context=None: uid,
	    }

	def onchange_status(self, cr, uid, ids, status, context=None): 
		if status:
			return {'value' : {'status1':status}}
	
class Induction(osv.osv):
	_name = 'induction'
	_rec_name='company_id'
	
	_columns = {
	
		'ind_id': fields.many2one('joining','Induction'),
		'company_id': fields.char('Company', required=True),
		'responsible':fields.many2one('hr.employee','Responsible',required=True),
		'remarks_id': fields.char("Remarks", required=True),
		}		
