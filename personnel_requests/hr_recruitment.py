# coding: utf-8
import time
from datetime import datetime, date
from openerp.osv import fields, osv

class hr_recruitment_request(osv.osv):
    _inherit = 'hr.recruitment.request'
    _columns = {

        'request_date': fields.datetime("Request Date"), 
        'job_grade': fields.integer('Job Grade'),
        'job_grade_pay': fields.integer('Job Grade Pay'),
        'proposed_position_pay': fields.integer('Proposed Position Pay'),        
        'additional_reason': fields.text('Reason for Additional Employees', required=True),
        'exiting_emp_name': fields.many2one('res.users', 'Name of Exiting Employee'),  
        'exit_date': fields.date('Exit Date'),  
        'reason_for_departure': fields.char('Reason for Departure'),
        'position_reporting_to': fields.many2one('res.users', 'Position Reporting to'),
        'temp_perm': fields.selection([('yes', 'Yes'),('draft', 'No')], 'Will Employee be on Permanent or Temporary terms?'),                                            
        'duration': fields.float('Duration (Months)'),  
        'emp_req_date': fields.date('Employee Required Date'),                  
        'current_head_count': fields.integer('Current Head Count in Department'), 
#        'tools_facility_req': fields.one2many('', '', 'Tools Facilities Required'), 
        'approved_head_count': fields.integer('Approved Head Count'),                 
        'position_in_budget': fields.selection([('yes', 'Yes'),('draft', 'No')], 'Is the position in this year’s budget?'),                   
        'full_year_budget': fields.float('Full Year Budget', readonly=False, states={'draft': [('readonly', True)]}),                                   
        'budget_balance_date': fields.float('Budget Balance to Date', readonly=False, states={'draft': [('readonly', True)]}),                                   
        'state': fields.selection([('draft', 'Draft'),
                                   ('hr_approval', 'Awaiting HR Approval'),
                                   ('finance_approval', 'Awaiting Finance Approval'),
                                   ('ceo_approval', 'Awaiting CEO Approval'),
                                   ('approved', 'Approved'),
                                   ('refused', 'Refused'),
                                   ],
                                  'State', readonly=True),
        }

    _defaults = {
        'request_date': fields.date.context_today,
        'state': 'draft'
    }
    

