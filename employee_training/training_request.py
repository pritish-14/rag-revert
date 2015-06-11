# coding: utf-8
# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
from datetime import datetime,date
from json import dumps
from openerp.exceptions import except_orm, Warning, RedirectWarning


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
                'employee_id':fields.many2one('hr.employee','Section Manager',readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'user_id':fields.many2one('res.users',"Employee", readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'section':fields.many2one('dep.section','Section',readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                #'section':fields.many('Section'),
                'department_id':fields.many2one('hr.department','Department',readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                #'request_date':fields.datetime('Request Date'),
                'training_date':fields.datetime('Training Date',readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'type':fields.selection(TRAINING_SELECTION, 'Training Type',required=True ,select=True, readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'name':fields.char('Training Request'),
                'title':fields.char('Training Title',required=True, readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'duration':fields.integer('Training Duration (Days)',required=True, readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                #'unknown_date':fields.date('Unknown',required=True),
                'venue':fields.char('Venue',required=True, readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'facilitator':fields.char('Training Facilitator',required=True, readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'sponsorship':fields.char('Sponsorship (if any)', readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'cost':fields.float('Training Cost',required=True, readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'travel_cost':fields.float('Travel Cost', readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'food_n_lodging':fields.float('Food & Lodging', readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'other_cost':fields.float('Any Other Costs', readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'highlight':fields.text('Training Highlights', readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'justification':fields.text('Training Justification',readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'annual_budget':fields.float('Annual Training Budget',readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'expenditure_to_date':fields.float  ('Expenditure to Date' ,readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'available_budget':fields.float('Available Training Budget',readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'captured_training':fields.selection(CAPTURED_TRAINING_SELECTION, 'Has this training captured as a training need?',select=True ,readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'included_training_plan':fields.selection(CAPTURED_TRAINING_SELECTION, 'Is the training included in the Training Plan for this staff?',select=True ,readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'bonding_required':fields.selection(CAPTURED_TRAINING_SELECTION, 'Bonding required?',select=True ,readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'dit_application':fields.selection(CAPTURED_TRAINING_SELECTION, 'DIT application (if applicable) done',select=True, readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'visa_obtained':fields.selection(CAPTURED_TRAINING_SELECTION, 'Visa (if applicable) obtained by applicant',select=True, readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'bonding_signed':fields.selection(CAPTURED_TRAINING_SELECTION, 'Bonding documents signed (if applicable)',select=True ,readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'hr_remarks':fields.text('HR Remarks' ,readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'state':fields.selection(STATE_SELECTION,'State',select=True ,readonly=False, states={'approved': [('readonly', True)],'refused': [('readonly', True)]}),
                'order_line': fields.one2many('training.line', 'training_id', 'Training Lines', readonly=True, states={'draft': [('readonly', False)], 'approved': [('readonly', True)]}),
                'refused_by': fields.many2one('res.users',"Refused By", readonly=True),
                'note': fields.text("Reson For Request"),
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
        line=self.browse(cr, uid, ids, context=context)
        user_id = self.pool.get('res.users').browse(cr, uid, uid, context).id
        print "======================", line.note
        if line.note is False:
            print '---------------------------',line.note        	
            raise Warning(_('Plaese first write Note for Reason'))
        else:  
            self.write(cr, uid, ids, {'state':'refused','refused_by': user_id}, context=context)
        return True

class Training_Lines(osv.osv):
    _name = 'training.line'
    _description = 'Training Lines'
    _columns = {
                'training_id':fields.many2one('training.request','Training Id'),
                'employee_id':fields.many2one('hr.employee','Employees',required=True),
                #'department_id':fields.many2one('hr.department','Departments')
                'job_title':fields.many2one('hr.job','Job Title',required=True),
                }
    def onchange_employee_id(self,cr, uid, ids, employee_id, context=None):
        emp_read = self.pool.get('hr.employee').browse(cr, uid, employee_id)
        res = {
            'department_id':emp_read.department_id,
            'job_title':emp_read.job_id,
        }
        return {'value':res}
