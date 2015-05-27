# -*- coding: utf-8 -*-
##################################################################################

import datetime
import time
from itertools import groupby
from operator import itemgetter
import logging

import math
from openerp import netsvc
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp import SUPERUSER_ID, tools
_logger = logging.getLogger(__name__)


class holiday_calendar_period(osv.osv):
    _name = "holiday.calendar.period"
    _description = "Holidays Calendar Period"
    _columns = {
        'name': fields.char('Holiday Name', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),
        'holiday_id': fields.many2one('hr.holidays.calendar', 'Holiday'),
    }

class holiday_calendar_year(osv.osv):
    _name = "holiday.calendar.year"
    _description = "Calendar Year"
    _columns = {
        'name': fields.char('Calendar Year', required=True)
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'There is already Calendar Year defined for this year!'),
    ]

class hr_holidays_calendar(osv.osv):
    _name = "hr.holidays.calendar"
    _description = "Holidays Calendar"
    _columns = {
        'name': fields.char('Description', required=True),
        'year_id': fields.many2one('holiday.calendar.year', 'Calendar Year', required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'period_ids': fields.one2many('holiday.calendar.period', 'holiday_id', 'Holiday Period')
    }

    _sql_constraints = [
        ('year_uniq', 'unique(year_id, company_id)', 'There is already Holiday Calendar defined for this Company!'),
    ]


class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    _description = "Leave Type"

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            res.append((record.id, name))
        return res

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        ids = super(hr_holidays_status, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=False)
        new_ids = []
        if not context.get('no_sick_list'):
            return ids
        for leave in self.browse(cr, uid, ids, context=context):
            if leave.name == 'Sick Leave':
                continue
            new_ids.append(leave.id)
        return new_ids

class ir_attachment(osv.Model):
    _inherit = 'ir.attachment'

    _columns = {
        'leave_id': fields.many2one('hr.holidays', 'Leave'),
        'note_type': fields.selection([('doctor','Doctor')], 'Note Type')
    }

class hr_holidays(osv.Model):
    _inherit = "hr.holidays"

    def _employee_get(self, cr, uid, context=None):        
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            return emp_id
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False
        
    def _approve_refuse(self, cr, uid, ids, name, args, context=None):
        res = {}
        invisible = False
        for line in self.browse(cr, uid, ids, context=context):
            if line.state == 'confirm' and line.employee_id.parent_id and line.employee_id.parent_id.user_id and uid == line.employee_id.parent_id.user_id.id:
                 invisible = True
            res[line.id] = invisible
        return res

    _columns = {
        'state': fields.selection([('draft', 'To Submit'),
                                    ('submit', 'Submit'),
                                    ('cancel', 'Cancelled'),
                                    ('confirm', 'Waiting Manager Apporval'),
                                    ('refuse', 'Refused'),
                                    ('validate1', 'Waiting for COO Approval'),
                                    ('validate2', 'Waiting for HR Approval'),
                                    ('validate', 'Approved')],
            'Status', readonly=True, track_visibility='onchange',
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.'),
        'attachment_ids': fields.one2many('ir.attachment', 'leave_id', 'Attachments', readonly=True, states={'draft':[('readonly',False)]}),
        'user_id':fields.related('employee_id', 'user_id', type='many2one', relation='res.users', string='User', store=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_from': fields.datetime('Start Date', readonly=True, states={'draft':[('readonly',False)]}, select=True),
        'date_to': fields.datetime('End Date', readonly=True, states={'draft':[('readonly',False)]}),
        'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type", required=True,readonly=True, states={'draft':[('readonly',False)]}),
        'employee_id': fields.many2one('hr.employee', "Employee", select=True, invisible=False, readonly=True, states={'draft':[('readonly',False)]}),
        'number_of_days_temp': fields.float('Allocation', readonly=True, states={'draft':[('readonly',False)]}),
        'number_of_days_temp1': fields.float('Allocation', readonly=True, states={'draft':[('readonly',False)]}),
        'category_id': fields.many2one('hr.employee.category', "Employee Tag", help='Category of Employee', readonly=True, states={'draft':[('readonly',False)]}),
        'holiday_type': fields.selection([('employee','By Employee'),('category','By Employee Tag')], 'Allocation Mode', readonly=True, states={'draft':[('readonly',False)]}, help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category', required=True),
        'allocation_from': fields.datetime('Start Date', readonly=True, states={'draft':[('readonly',False)]}, select=True),
        'allocation_to': fields.datetime('End Date', readonly=True, states={'draft':[('readonly',False)]}),
        'sequence': fields.char('Sequence', size=64, readonly=True),

        'approve_refuse_invisible': fields.function(_approve_refuse, type='boolean', string='Invisible'),
        #AREQ, Leave: LREQ/
    }

    _defaults = {
        'state': 'draft',
        'employee_id': lambda obj, cr, uid, context: uid,
        'user_id': lambda obj, cr, uid, context: uid,
        'holiday_type': 'employee'
    }

    def check_allocation_request(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        if not ids:
            filters = [('state', '=', 'validate'), ('type', '=', 'add')]
            ids = self.search(cr, uid, filters, context=context)
        res = None
        try:
            if ids:
                for allocation in self.browse(cr, uid, ids, context=context):
                    current_date = fields.date.context_today(self, cr, uid, context=context)
                    if allocation.allocation_to:
                        allocation_date = allocation.allocation_to.split(' ')[0]
                        if allocation_date < current_date:
                            self.write(cr, uid, [allocation.id], {'number_of_days_temp': 0.0})
        except Exception:
            _logger.exception("Failed processing allocation request")
        return res

    def write(self, cr, uid, ids, vals, context=None):
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.holiday_status_id.name == 'Sick Leave':
                user_ids = self.pool.get('res.users').search(cr, uid, [('login','=', '640')])
                if user_ids:
                    self.message_subscribe_users(cr, uid, [holiday.id], user_ids=user_ids, context=context)
            else:
                user_ids = self.pool.get('res.users').search(cr, uid, [('login','=', '569')])
                if user_ids:
                    self.message_subscribe_users(cr, uid, [holiday.id], user_ids=user_ids, context=context)

        return super(hr_holidays, self).write(cr, uid, ids, vals, context=context)

    def check_sick_leave(self, cr, uid, ids, context=None):
        for leave in self.browse(cr, uid, ids, context=context):
            if leave.type != 'add' and leave.holiday_status_id.name == 'Sick Leave':
                return True
        return False

    def get_holidays_list(self, cr, uid, ids, date_from, date_to):
        holiday_count = 0
        interval = date_to - date_from
        dt_range = []
        period_range = []
        [dt_range.append((date_from + datetime.timedelta(days=x)).strftime('%Y-%m-%d')) for x in range(int(interval.days + 1))]
        for dt in dt_range:
            date = datetime.datetime.strptime(dt , '%Y-%m-%d')
            year_id = self.pool.get('holiday.calendar.year').search(cr, uid, [('name', '=', str(date.year))])
            if year_id:
                holiday_id = self.pool.get('hr.holidays.calendar').search(cr, uid, [('year_id', '=', year_id[0])])
                if holiday_id:
                    holiday = self.pool.get('hr.holidays.calendar').browse(cr, uid, holiday_id[0])
                    for period in holiday.period_ids:
                        DATETIME_FORMAT = "%Y-%m-%d"
                        pfrom = datetime.datetime.strptime(period.date_start, DATETIME_FORMAT)
                        pto = datetime.datetime.strptime(period.date_end, DATETIME_FORMAT)
                        holiday_period = pto - pfrom
                        for x in range(int(holiday_period.days + 1)):
                            holiday_date = (pfrom + datetime.timedelta(days=x)).strftime('%Y-%m-%d')
                            if dt == holiday_date:
                                holiday_count += 1
        return holiday_count
    # TODO: can be improved using resource calendar method
    def _get_number_of_days(self, cr, uid, ids, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        DATETIME_FORMAT = "%Y-%m-%d"

        date_from = date_from.split(' ')[0]
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        date_to = date_to.split(' ')[0]
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        to_date = to_dt + datetime.timedelta(hours=23)
        calendar_ids = self.pool.get('resource.calendar').search(cr, uid, [])
        if not calendar_ids:
            raise osv.except_osv(_('Warning!'),_('Resource Working Calendar is missing. It needs to be created.'))
        hours_start_end = self.pool.get('resource.calendar').interval_hours_get(cr, uid, calendar_ids[0], from_dt, to_date)
        cal = self.pool.get('resource.calendar').browse(cr, uid, calendar_ids[0])
        working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, cal, from_dt)
#        if from_dt == to_dt:
#            days = 1
        #else:
        days = hours_start_end / (working_hours_on_day or 9)
        holidays =self.get_holidays_list(cr, uid, ids, from_dt, to_date)
        total = days - holidays
        return total

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            #date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            result['value']['date_to'] = str(date_from)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(cr, uid, ids, date_from, date_to)
            #result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))
            result['value']['number_of_days_temp1'] = round(math.floor(diff_day))
        else:
            result['value']['number_of_days_temp'] = 0
            result['value']['number_of_days_temp1'] = 0

        return result

    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(cr, uid, ids, date_from, date_to)
            #result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))
            result['value']['number_of_days_temp1'] = round(math.floor(diff_day))
        else:
            result['value']['number_of_days_temp'] = 0
            result['value']['number_of_days_temp1'] = 0

        return result

    def holidays_refuse(self, cr, uid, ids, context=None):
        allow_group = []
        coo_group = self.pool.get('ir.model.data').get_object(cr, uid, 'employee_joining', 'group_coo_emp')
        coo_users = [user.id for user in coo_group.users]
        allow_group.extend(coo_users)

        man_group = self.pool.get('ir.model.data').get_object(cr, uid, 'base', 'group_hr_manager')
        man_users = [user.id for user in man_group.users]
        allow_group.extend(man_users)

        for record in self.browse(cr, uid, ids):
            if uid != record.employee_id.parent_id.user_id.id and uid not in allow_group:
                raise osv.except_osv(_('Warning!'),_('Only manager of this employee can refuse the leave.'))
        return super(hr_holidays, self).holidays_refuse(cr, uid, ids, context=context)

    def holidays_first_validate(self, cr, uid, ids, context=None):
        allow_group = []
        coo_group = self.pool.get('ir.model.data').get_object(cr, uid, 'employee_joining', 'group_coo_emp')
        coo_users = [user.id for user in coo_group.users]
        allow_group.extend(coo_users)

        man_group = self.pool.get('ir.model.data').get_object(cr, uid, 'base', 'group_hr_manager')
        man_users = [user.id for user in man_group.users]
        allow_group.extend(man_users)
        for record in self.browse(cr, uid, ids):
            if uid != record.employee_id.parent_id.user_id.id and uid not in allow_group:
                raise osv.except_osv(_('Warning!'),_('Only manager of this employee can approve the leave.'))

            obj_emp = self.pool.get('hr.employee')
            ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
            manager = ids2 and ids2[0] or False

            if record.holiday_status_id.name == 'Sick Leave':
                return self.write(cr, uid, ids, {'state':'validate2', 'manager_id': manager})
            else:
                return self.write(cr, uid, ids, {'state':'validate1', 'manager_id': manager})

            if record.type == 'add':
                return self.write(cr, uid, ids, {'state':'validate'})

        self.holidays_first_validate_notificate(cr, uid, ids, context=context)
        return True

    def holidays_second_validate_notificate(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            self.message_post(cr, uid, [obj.id],
                _("Leave Request approved"), context=context)

    def holidays_validate(self, cr, uid, ids, context=None):
        allow_group = []
        coo_group = self.pool.get('ir.model.data').get_object(cr, uid, 'employee_joining', 'group_coo_emp')
        coo_users = [user.id for user in coo_group.users]
        allow_group.extend(coo_users)

        man_group = self.pool.get('ir.model.data').get_object(cr, uid, 'base', 'group_hr_manager')
        man_users = [user.id for user in man_group.users]
        allow_group.extend(man_users)

        manager_group = self.pool.get('ir.model.data').get_object(cr, uid, 'project', 'group_project_manager')

        for record in self.browse(cr, uid, ids):
            if uid in allow_group:
                self.message_subscribe_users(cr, uid, [record.id], user_ids=[uid], context=context)
            if record.type == 'add':
                return self.write(cr, uid, ids, {'state':'validate'})

            if uid != record.employee_id.parent_id.user_id.id and uid not in allow_group:
                raise osv.except_osv(_('Warning!'),_('Only manager of this employee can approve the leave.'))
        self.holidays_first_validate_notificate(cr, uid, ids, context=context)
        return super(hr_holidays, self).holidays_validate(cr, uid, ids, context=context)

    def action_submit(self, cr, uid, ids, context=None):
        if context is None: context = {}
        holi_status_obj = self.pool.get('hr.holidays.status')
        wf_service = netsvc.LocalService("workflow")
        for record in self.browse(cr, uid, ids):
            if not record.employee_id and record.employee_id.parent_id:
                raise osv.except_osv(_('Warning!'),_('Please assign manager of this employee in Employee form.'))
            if not record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                raise osv.except_osv(_('Warning!'),_('Please assign user in this employee manager.'))

            if record.type=='remove':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'hr.holidays.lreq') or ''
            elif record.type=='add':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'hr.holidays.areq') or ''

            number_of_days_temp = 0
            number_of_days_temp1 = 0

            if (record.date_to and record.date_from) and (record.date_from <= record.date_to):
                diff_day = self._get_number_of_days(cr, uid, ids, record.date_from, record.date_to)
                number_of_days_temp = round(math.floor(diff_day))
                number_of_days_temp1 = round(math.floor(diff_day))

            self.write(cr, uid, [record.id], {'state': 'submit', 'sequence': sequence, 'number_of_days_temp':number_of_days_temp, 'number_of_days_temp1': number_of_days_temp1}, context=context)
            if record.holiday_type == 'employee' and record.holiday_status_id.name == 'Sick Leave' and record.type == 'remove':
                if not record.attachment_ids:
                    raise osv.except_osv(_('Warning!'),_('You have to add atleast one attachment for Sick Leave detail.'))
                leaves_rest_sick = holi_status_obj.get_days( cr, uid, [record.holiday_status_id.id], record.employee_id.id, False)[record.holiday_status_id.id]['remaining_leaves']
                if leaves_rest_sick < record.number_of_days_temp:
                    try:
                        view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_holidays_extension', 'leave_check_view')[1]
                    except ValueError:
                        view_id = False
                    ctx = dict(context)
                    ctx.update({
                        'active_model': 'hr.holidays',
                        'active_id': record.id,
                        'sick_leave_count': record.number_of_days_temp,
                        'remaining_sick_leave': leaves_rest_sick,
                        'employee_id': record.employee_id.id
                    })

                    return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'wizard.leave.check',
                    'views': [(view_id, 'form')],
                    'view_id': view_id,
                    'target': 'new',
                    'context': ctx,
                }
            else:
                self.write(cr, uid, [record.id], {'state': 'confirm'})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
