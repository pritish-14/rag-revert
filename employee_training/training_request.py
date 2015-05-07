# coding: utf-8
# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
from datetime import datetime,date
from json import dumps

class Training_Request(osv.osv):
    _name = 'training.request'
    _inherit = 'mail.thread'
    _description = 'Trainig Request'

    TRAINING_SELECTION = [
        ('internal', 'Internal'),
        ('external', 'External')
    ]
    CAPTURED_TRAINING_SELECTION = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('na','N/A')
    ]
    STATE_SELECTION = [
                 ('draft','Draft'),
                 ('awaiting_hod_approval','Awaiting HOD Approval'),
                 ('awaiting_hr_approval','Awaiting HR Approval'),
                 ('awaiting_finance_approval','Awaiting Finance Approval'),
                 ('awaiting_ceo_approval','Awaiting CEO Approval'),
                 ('approved','Approved'),
                 ('refused','Refused'),
                 ]
    
   
    def _current_employee_get(self, cr, uid, context=None):
         ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
         if ids:
             return ids[0]
         return False
    
    _columns = {
                'employee_id':fields.many2one('hr.employee','Section Manager'),
                'user_id':fields.many2one('res.users',"Employee"),
                'section':fields.many2one('dep.section','Section'),
                #'section':fields.many('Section'),
                'department_id':fields.many2one('hr.department','Department'),
                #'request_date':fields.datetime('Request Date'),
                'training_date':fields.datetime('Training Date'),
                'type':fields.selection(TRAINING_SELECTION, 'Training Type',required=True ,select=True),
                'name':fields.char('Training Request'),
                'title':fields.char('Training Title',required=True),
                'duration':fields.date('Training Duration',required=True),
                #'unknown_date':fields.date('Unknown',required=True),
                'venue':fields.char('Venue',required=True),
                'facilitator':fields.char('Training Facilitator',required=True),
                'sponsorship':fields.char('Sponsorship (if any)',required=True),
                'cost':fields.float('Training Cost',required=True),
                'travel_cost':fields.float('Travel Cost'),
                'food_n_lodging':fields.float('Food & Lodging'),
                'other_cost':fields.float('Any Other Costs'),
                'highlight':fields.text('Training Highlights'),
                'justification':fields.text('Training Justification'),
                'annual_budget':fields.float('Annual Training Budget'),
                'expenditure_to_date':fields.float  ('Expenditure to Date'),
                'available_budget':fields.float('Available Training Budget'),
                'captured_training':fields.selection(CAPTURED_TRAINING_SELECTION, 'Has this training captured as a training need?',select=True),
                'included_training_plan':fields.selection(CAPTURED_TRAINING_SELECTION, 'Is the training included in the Training Plan for this staff?',select=True),
                'bonding_required':fields.selection(CAPTURED_TRAINING_SELECTION, 'Bonding required?',select=True),
                'dit_application':fields.selection(CAPTURED_TRAINING_SELECTION, 'DIT application (if applicable) done',select=True),
                'visa_obtained':fields.selection(CAPTURED_TRAINING_SELECTION, 'Visa (if applicable) obtained by applicant',select=True),
                'bonding_signed':fields.selection(CAPTURED_TRAINING_SELECTION, 'Bonding documents signed (if applicable)',select=True),
                'hr_remarks':fields.text('HR Remarks'),
                'state':fields.selection(STATE_SELECTION,'State',select=True),
                'order_line': fields.one2many('training.line', 'training_id', 'Training Lines', readonly=True, states={'draft': [('readonly', False)], 'approved': [('readonly', False)]}),
                }
    _defaults={
               'state':'draft',
               'employee_id':_current_employee_get,
               'user_id': lambda self, cr, uid, context=None: uid,
               }
    
    #def onchange_employee_id(self,cr, uid, ids, employee_id, context=None):
    '''emp_read = self.pool.get('hr.employee').read(cr, uid, employee_id, ['department_id','company_id'], context=context)
        res = {
               'department_id':emp_read.get('department_id') and emp_read.get('department_id')[0],
               'company_id':emp_read.get('company_id') and emp_read.get('company_id')[0],
                }'''
    '''emp_read = self.pool.get('hr.department').browse(cr, uid, employee_id)
        print"------------------------------",emp_read        
        res = {
               'employee_id':emp_read.manager_id,
               'section': emp_read.section_ids,
               #'department_id':emp_read.department_id,
               #'company_id':emp_read.company_id,
                }        
        return {'value':res}'''
    
    
    def onchange_employee_id(self,cr, uid, ids, employee_id, context=None):
        emp_read = self.pool.get('hr.employee').browse(cr, uid, employee_id)        
        res = {
               'department_id':emp_read.department_id,
               #'section':emp_read.section,
                }
        return {'value':res}
    
    def state_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True
    
    def state_awaiting_finance(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'awaiting_finance_approval'}, context=context)
        return True
    
    def state_awaiting_hr(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'awaiting_hr_approval'}, context=context)
        return True
    
    def state_awaiting_hod(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'awaiting_hod_approval','name':self.pool.get('ir.sequence').get(cr, uid, 'training.request') or '/'}, context=context)
        return True
    
    def state_awaiting_ceo(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'awaiting_ceo_approval'}, context=context)
        return True
    def state_approved(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'approved'}, context=context)
        return True
    
    def state_refused(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'refused'}, context=context)
        return True

class Training_Lines(osv.osv):
    _name = 'training.line'
    _description = 'Training Lines'
    _columns = {
                'training_id':fields.many2one('training.request','Training Id'),
                'employee_id':fields.many2one('hr.employee','Employees'),
                #'department_id':fields.many2one('hr.department','Departments')
                'job_title':fields.many2one('hr.job','Job Title'),
                }
    def onchange_employee_id(self,cr, uid, ids, employee_id, context=None):
        emp_read = self.pool.get('hr.employee').browse(cr, uid, employee_id)
        res = {
            'department_id':emp_read.department_id,
            'job_title':emp_read.job_id,
        }
        return {'value':res}
