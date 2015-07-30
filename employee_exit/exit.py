# coding: utf-8
# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
from datetime import datetime,date
from json import dumps
import re
from dateutil.relativedelta import relativedelta

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
                 ('retrenchment','Retrenchment'),
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
                 'state':fields.selection(STATES,'State',),
                 'staff_no':fields.integer('Staff No.'),
                 'emp_date':fields.date('Employment Date'),
                 'company_id':fields.many2one('res.company','Company'),
                 'empolymnt_date':fields.date("Employment Date"),
                 'service_date': fields.char("SErvice Date"),
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
            'staff_no':emp_read.staff_no,
            'emp_date':emp_read.employment_date,
            'company_id':emp_read.company_id,
            'empolymnt_date':emp_read.employment_date,
        }
        return {'value':res}

 
    def onchange_exit_date(self,cr,uid,ids,exit_date,context=None):
        read_value=self.browse(cr, uid, ids, context)
        print "addsdsdf----------------------------------",read_value.empolymnt_date
        if exit_date:
            exit_date = datetime.strptime(str(exit_date), '%Y-%m-%d')
            delta = relativedelta(exit_date, read_value.empolymnt_date)
            #deceased = ''
            years_months_days = str(delta.years) + 'year ' \
                    + str(delta.months) + 'month '
            val = {
	            'service_date':	years_months_days,
	            }
            return {'value': val}                    
        else:
            years_months_days = 'plz fill !'

        # Return the age in format y m d when the caller is the field name
            val = {
	            'service_date':	years_months_days,
	            }
            return {'value': val}     
        
    
    def state_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True
    
    def state_in_progress(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'in_progress','name':self.pool.get('ir.sequence').get(cr, uid, 'exit') or '/'}, context=context)
        return True
    
    def state_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context=context)
        return True
