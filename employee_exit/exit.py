# coding: utf-8
# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
from datetime import datetime,date
from json import dumps

class Exit(osv.osv):
    _name = 'exit'
    _description = 'Exit'
    _inherit = 'mail.thread'
    STATES = [
              ('draft','Draft'),
              ('in_progress','In Progress'),
              ('done','Done')
              ]
    EXIT_TYPE = [
                 ('registration','Resignation'),
                 ('termination','Termination'),
                 ('summary_dismissal','Summary Dismissal'),
                 ('probationary_termination','Probationary Termination'),
                 ('redundancy','Redundancy'),
                 ('restructuring','Restructuring'),
                 ('early_retirement','Early Retirement'),
                 ('retirement','Retirement'),
                 ('death','Death')
                 ]
    MEDICAL_STATUS = [
                      ('yes_cancelled','Yes Cancelled'),
                      ('cover_not_utilized','Cover not utilized'),
                      ('no_cover','No Cover'),
                      ]
    
    def _current_employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False
        
    _columns = {
                 'employee_id':fields.many2one('hr.employee','Employee',required=True),
                 'job_id':fields.many2one('hr.job','Job Title',required=True),
                 'department_id':fields.many2one('hr.department','Department',required=True),
                 'type':fields.selection(EXIT_TYPE,'Exit Type',required=True),
                 'name':fields.char('Exit Reference'),
                 'notification_date':fields.date('Exit Notification Date',required=True),
                 'interview_date':fields.date('Exit Interview Date'),
                 'clearence_date':fields.date('Clearance Date',required=True),
                 'exit_date':fields.date('Exit Date'),
                 'medical_status':fields.selection(MEDICAL_STATUS,'Medical Cover Status',required=True),
                 'notice_pay_recv':fields.char('Notice Pay Received',required=True),
                 'emp_cert_issued':fields.selection([('yes','Yes'),('no','No')],'Employment Certification Issued',required=True),
                 'state':fields.selection(STATES,'State',)
                 }
    _defaults = {
        #'employee_id': _current_employee_get,
        }
        
        
        
    _track = {
        'state': {
            'employee_exit.mt_alert_request_exit_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'employee_exit.mt_alert_request_exit_in_progress': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'in_progress',
            'employee_exit.mt_alert_request_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
        },
    }
	
	
    def onchange_employee_id(self,cr, uid, ids, employee_id, context=None):
        emp_read = self.pool.get('hr.employee').browse(cr, uid, employee_id)
        res = {
            'department_id':emp_read.department_id,
            'job_id':emp_read.job_id,
        }
        return {'value':res}    
    
    def state_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True
    
    def state_in_progress(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'in_progress','name':self.pool.get('ir.sequence').get(cr, uid, 'exit') or '/'}, context=context)
        return True
    
    def state_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context=context)
        return True
