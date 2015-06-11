# coding: utf-8
# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.

from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
from datetime import datetime,date
from json import dumps
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Medical_Premium(osv.osv):
    _name = 'medical.premium'
    _description = 'Medical Premium'
    _inherit = ['mail.thread']
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('awaiting_finance','Awaiting Finance Confirmation'),
        ('awaiting_hr', 'Awaiting HR Approval'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('confirmed', 'Rejected')
    ]
    
    def _current_employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False
    
    _columns = {
                'name':fields.char('Medical Premium Request'),
                'employee_id':fields.many2one('hr.employee','Employee',required=True),
                'department_id':fields.many2one('hr.department','Department',required=True),
                'company_id':fields.many2one('res.company','Company',required=True),
                'request_date':fields.date('Request Date',required=True),
                'dependents_table':fields.one2many('dep.table','dpmn_t',"Dependents Table"),
                'date_of_cover':fields.date('Effective Date of Cover',required=True),
                'premium':fields.float('Premium Amount',required=True),
                'recovery':fields.float('Recovery Tenure(Months)',required=True),
                'recovery_date':fields.date('Recovery Start Date'),
                'state': fields.selection(STATE_SELECTION, 'Status', select=True),
                'reject_by': fields.many2one('res.users',"Reject By", readonly=True),
                'note': fields.text("Reson For Request"),
                }
    _defaults = {
                 'request_date':str(date.today()),
                 'state': 'draft',
                 #'employee_id': lambda self, cr, uid, context=None: uid,
                 'employee_id': _current_employee_get,
                 #'employee_id': "abc",
                 }
                 
    
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'medical.premium') or '/'
        return super(Medical_Premium, self).create(cr, uid, vals, context=context)
        
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'request_date': fields.date.context_today(self, cr, uid, context=context),
            'state': 'draft',
            'recovery_date': False,
            'name': self.pool.get('ir.sequence').get(cr, uid, 'medical.premium'),
        })
        return super(Medical_Premium, self).copy(cr, uid, id, default, context=context)
    def onchange_employee_id(self,cr, uid, ids, employee_id, context=None):
        '''emp_read = self.pool.get('hr.employee').read(cr, uid, employee_id, ['department_id','company_id'], context=context)
        res = {
               'department_id':emp_read.get('department_id') and emp_read.get('department_id')[0],
               'company_id':emp_read.get('company_id') and emp_read.get('company_id')[0],
                }'''
        emp_read = self.pool.get('hr.employee').browse(cr, uid, employee_id)        
        res = {
               'department_id':emp_read.department_id,
               'company_id':emp_read.company_id,
                }        
        return {'value':res}
        
    
    def state_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True
    
    def state_awaiting_finance(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'awaiting_finance'}, context=context)
        return True
    
    def state_awaiting_hr(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'awaiting_hr'}, context=context)
        return True
    
    def state_approved(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'approved'}, context=context)
        return True
    
    def state_refused(self, cr, uid, ids, context=None):
        line=self.browse(cr, uid, ids, context=context)
        user_id = self.pool.get('res.users').browse(cr, uid, uid, context).id
        print "======================", line.note
        if line.note is False:
            print '---------------------------',line.note        	
            raise Warning(_('Plaese first write Note for Reason'))
        else:   
            self.write(cr, uid, ids, {'state':'refused','reject_by': user_id}, context=context)
        return True
    
    def state_confirmed(self, cr, uid, ids, context=None):
        line=self.browse(cr, uid, ids, context=context)
        user_id = self.pool.get('res.users').browse(cr, uid, uid, context).id
        if line.note is False:
            print '---------------------------',line.note        	
            raise Warning(_('Plaese first write Note for Reason'))
        else:   
            self.write(cr, uid, ids, {'state':'confirmed','reject_by': user_id}, context=context)
        return True
        
       
       
class Dependents_Tables(osv.osv):
    _name = 'dep.table'
    _rec_name= 'name_id'
    _columns = {
                'dpmn_t': fields.many2one("medical.premium","REFRENCES"),
                'name_id': fields.char("Name"),
                }
                
  
    
