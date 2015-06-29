#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class hr_job(osv.Model):

    _name = 'hr.job'
    _inherit = 'hr.job'

    _columns = {
        'max_employees': fields.integer('Maximum Number of Employees'),
        'max_employees_fuzz': fields.integer('Expected Turnover',
                                             help="Recruitment module will allow you to \
                                                  create this number of additional applicants and \
                                                  contracts above the maximum value. Use this \
                                                  number as a buffer to have additional \
                                                  employees on hand to cover employee turnover."),
    }

    # Do not write negative values for no. of recruitment
    def write(self, cr, uid, ids, vals, context=None):

        value = vals.get('no_of_recruitment', False)
        if value and value < 0:
            vals['no_of_recruitment'] = 0

        return super(hr_job, self).write(cr, uid, ids, vals, context=context)


class hr_applicant(osv.Model):

    _name = 'hr.applicant'
    _inherit = 'hr.applicant'

    def create(self, cr, uid, vals, context=None):

        if vals.get('job_id', False):
            data = self.pool.get('hr.job').read(cr, uid, vals['job_id'],
                                                ['max_employees', 'no_of_employee', 'state',
                                                 'max_employees_fuzz'],
                                                context=context)
            if data.get('state', False):
                if data['state'] != 'recruit' and int(data['no_of_employee']) >= (int(data['max_employees']) + data['max_employees_fuzz']):
                    raise osv.except_osv(_('Job not open for recruitment!'),
                                         _('You may not register applicants for jobs that are not recruiting.'))

        return super(hr_applicant, self).create(cr, uid, vals, context=context)

    _columns = {
    	'job_max_pay': fields.float('Job Group Pay (Max)'),
        'job_min_pay': fields.float('Job Group Pay (Min)'),
        }

class hr_recruitment_request(osv.Model):

    _name = 'hr.recruitment.request'
    _description = 'Request for recruitment of additional personnel'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
    
         'reson_recruitment': fields.selection([('add_staff','Additional Staff'),('replace','Replacement'),('new_pos','New Postion')],'Reason For Recruitment'),     
        'request_no': fields.char('Recruitment Request'),    
        'name': fields.char('Description', size=64),
        'user_id': fields.many2one('res.users', 'Requesting User', required=True),
        'department_id': fields.many2one('hr.department', 'Department', related='job_id.department_id', store=True, readonly=True),
        'job_id': fields.many2one('hr.job', 'Vacant Job Title', required=True),
        'number': fields.integer('Number to Recruit', required=True),
        'current_number': fields.related('job_id', 'no_of_employee', type='integer', string="Current Number of Employees", readonly=True),
        'max_number': fields.related('job_id', 'max_employees', type='integer', string="Maximum Number of Employees", readonly=True),
        'reason': fields.text('Reason for Request'),
        'refused_by': fields.many2one('res.users',"Refused By", readonly=True),
        'note': fields.text("Reson For Request"),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirm', 'Confirmed'),
                                   ('exception', 'Exception'),
                                   ('recruitment', 'In Recruitment'),
                                   ('decline', 'Declined'),
                                   ('done', 'Done'),
                                   ('cancel', 'Cancelled'),
                                   ],
                                  'State', readonly=True),
        
    }

    _order = 'department_id, job_id'

    _defaults = {
        'number': 1,
        'user_id': lambda self, cr, uid, context=None: uid,
        'reson_recruitment': 'add_staff',
    }

    _track = {
        'state': {
            'hr_labour_recruitment.mt_alert_request_hr_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'hr_approval',
            'hr_labour_recruitment.mt_alert_request_finance_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'finance_approval',
            'hr_labour_recruitment.mt_alert_request_ceo_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'ceo_approval',
            'hr_labour_recruitment.mt_alert_request_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
            'hr_labour_recruitment.mt_alert_request_declined': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'refused',
        },
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('request_no','/')=='/':
            vals['request_no'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.recruitment.request') or '/'
        request =  super(hr_recruitment_request, self).create(cr, uid, vals, context=context)
        return request

    def onchange_job(self, cr, uid, ids, job_id, context=None):

        res = {'value': {'deparment_id': False, 'name': False}}
        if job_id:
            data = self.pool.get('hr.job').read(
                cr, uid, job_id, ['name', 'department_id'], context=context)
            if data.get('department_id', False):
                res['value']['department_id'] = data['department_id'][0]
            res['value']['name'] = 'Personnel Request: ' + str(data['name'])

        return res

    def _needaction_domain_get(self, cr, uid, context=None):

        users_obj = self.pool.get('res.users')

        domain = []
        has_prev_domain = False
        if users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            domain = [('state', '=', 'recruitment')]
            has_prev_domain = True
        if users_obj.has_group(cr, uid, 'hr_security.group_hr_director'):
            if has_prev_domain:
                domain = ['|'] + domain
            domain = domain + [('state', 'in', ['confirm', 'exception'])]

        if len(domain) == 0:
            return False

        return domain

    def condition_exception(self, cr, uid, ids, context=None):

        for req in self.browse(cr, uid, ids, context=context):
            if req.number + req.job_id.expected_employees > req.job_id.max_employees:
                return True

        return False

    def _state(self, cr, uid, ids, state, context=None):

        job_obj = self.pool.get('hr.job')

        for req in self.browse(cr, uid, ids, context=context):

            if state == 'recruitment':
                job_obj.write(cr, uid, req.job_id.id, {
                              'no_of_recruitment': req.number}, context=context)
                job_obj.job_recruitement(cr, uid, [req.job_id.id])
            elif state in ['done', 'cancel']:
                job_obj.job_open(cr, uid, [req.job_id.id])

            self.write(cr, uid, req.id, {'state': state}, context=context)

        return True

    def _state_subscribe_users(self, cr, uid, ids, state, context=None):

        imd_obj = self.pool.get('ir.model.data')
        model, group1_id = imd_obj.get_object_reference(
            cr, uid, 'base', 'group_hr_manager')
        model, group2_id = imd_obj.get_object_reference(
            cr, uid, 'hr_security', 'group_hr_director')
        data = self.pool.get('res.groups').read(
            cr, uid, [group1_id, group2_id], ['users'], context=context)
        user_ids = list(set(data[0]['users'] + data[1]['users']))
        self.message_subscribe_users(
            cr, uid, ids, user_ids=user_ids, context=context)

        return self._state(cr, uid, ids, state, context=context)

    def signal_confirm(self, cr, uid, ids, context=None):

        return self._state_subscribe_users(cr, uid, ids, 'hr_approval', context=context)

    def signal_finance_approve(self, cr, uid, ids, context=None):

        return self._state_subscribe_users(cr, uid, ids, 'finance_approval', context=context)

    def signal_ceo_approve(self, cr, uid, ids, context=None):

        return self._state_subscribe_users(cr, uid, ids, 'ceo_approval', context=context)

    def signal_approval(self, cr, uid, ids, context=None):

        return self._state(cr, uid, ids, 'approved', context=context)

    def signal_refuse(self, cr, uid, ids, context=None):
        line=self.browse(cr, uid, ids, context=context)
        user_id = self.pool.get('res.users').browse(cr, uid, uid, context).id
        print "======================", line.note
        if line.note is False:
            print '---------------------------',line.note        	
            raise Warning(_('Plaese first write Note for Reason'))
        else: 
            self.write(cr, uid, ids, {'state':'refused','refused_by': user_id}, context=context)
        return True
        
        
