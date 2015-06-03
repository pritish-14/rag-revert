import datetime
import math
import time
from operator import attrgetter

from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

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


class hr_holidays(osv.osv):
    _inherit = "hr.holidays"
    _track = {
        'state': {
            'hr_holidays.mt_holidays_approved': lambda self, cr, uid, obj, ctx=None: obj.state == 'validate',
            'hr_holidays.mt_holidays_refused': lambda self, cr, uid, obj, ctx=None: obj.state == 'refuse',
            'hr_holidays.mt_holidays_confirmed': lambda self, cr, uid, obj, ctx=None: obj.state == 'confirm',
        },
    }
    
    _columns = {
        'name': fields.char('Description', size=64),
        'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'Waiting Manager Apporval'), ('refuse', 'Refused'), ('validate1', 'Waiting Department Manager Apporval'), ('validate2', 'Waiting HR Manager Apporval'), ('validate3', 'Waiting CEO Apporval'), ('validate', 'Approved')],
            'Status', readonly=True, track_visibility='onchange', copy=False,
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.'),
        'attachment_ids': fields.one2many('ir.attachment', 'leave_id', 'Attachments', readonly=True, states={'draft':[('readonly',False)]}),
        'user_id':fields.related('employee_id', 'user_id', type='many2one', relation='res.users', string='User', store=True),
        'date_from': fields.datetime('Start Date', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, select=True, copy=False),
        'date_to': fields.datetime('End Date', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, copy=False),
        'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type", required=True,readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'employee_id': fields.many2one('hr.employee', "Employee", select=True, invisible=False, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'manager_id': fields.many2one('hr.employee', 'First Approval', invisible=False, readonly=True, copy=False,
                                      help='This area is automatically filled by the user who validate the leave'),
        'notes': fields.text('Reasons',readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'number_of_days_temp': fields.float('Allocation', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, copy=False),
        'meeting_id': fields.many2one('calendar.event', 'Meeting'),
        'type': fields.selection([('remove','Leave Request'),('add','Allocation Request')], 'Request Type', required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, help="Choose 'Leave Request' if someone wants to take an off-day. \nChoose 'Allocation Request' if you want to increase the number of leaves available for someone", select=True),
        'parent_id': fields.many2one('hr.holidays', 'Parent'),
        'linked_request_ids': fields.one2many('hr.holidays', 'parent_id', 'Linked Requests',),
        'department_id':fields.related('employee_id', 'department_id', string='Department', type='many2one', relation='hr.department', readonly=True, store=True),
        'category_id': fields.many2one('hr.employee.category', "Employee Tag", help='Category of Employee', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'relative': fields.selection([('father','Father'),('mother','Mother'),('children','Children'),('spouse','Spouse')], 'Relative', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'holiday_type': fields.selection([('employee','By Employee'),('category','By Employee Tag')], 'Allocation Mode', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category', required=True),
        
        'manager_id2': fields.many2one('hr.employee', 'Second Approval', readonly=True, copy=False,
                                       help='This area is automaticly filled by the user who validate the leave with second level (If Leave type need second validation)'),
        'double_validation': fields.related('holiday_status_id', 'double_validation', type='boolean', relation='hr.holidays.status', string='Apply Double Validation'),
    }
    _defaults = {
        'state': 'draft',
    }

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
        holidays =self.get_holidays_list(cr, uid, ids, from_dt, to_date)
        if from_dt == to_dt:
            days = 1
            total = days - holidays            
        else:
            days = hours_start_end / (working_hours_on_day or 9)
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

    def holidays_confirm(self, cr, uid, ids, context=None):
        if context is None: context = {}
        holi_status_obj = self.pool.get('hr.holidays.status')
        for record in self.browse(cr, uid, ids):
            if not record.employee_id and record.employee_id.parent_id:
                raise osv.except_osv(_('Warning!'),_('Please assign manager of this employee in Employee form.'))
            if not record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                raise osv.except_osv(_('Warning!'),_('Please assign user in this employee manager.'))

            if record.type=='remove':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'hr.holidays.lreq') or ''
            elif record.type=='add':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'hr.holidays.areq') or ''

            if record.holiday_type == 'employee' and record.holiday_status_id.name == 'Compassionate Leave' and record.type == 'remove':
                if not record.notes and record.relative:
                    raise osv.except_osv(_('Warning!'),_('You have to add reason as notes and chose relative in .'))                                                      
            elif record.holiday_type == 'employee' and record.holiday_status_id.name == 'Study Leave' and record.type == 'remove':
                if not record.attachment_ids:
                    raise osv.except_osv(_('Warning!'),_('You have to add atleast one attachment for Study Leave detail.'))
            elif record.holiday_type == 'employee' and record.holiday_status_id.name == 'Sick Leave' and record.type == 'remove':
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

    def holidays_approve(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id], context=context)
        return self.write(cr, uid, ids, {'state': 'validate3'})
        
    def holidays_first_validate(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.holidays_first_validate_notificate(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state':'validate1', 'manager_id': manager})

    def holidays_second_validate(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.holidays_first_validate_notificate(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state':'validate2', 'manager_id': manager})                        
        return True

    def holidays_validate(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        for record in self.browse(cr, uid, ids):
            if record.holiday_type == 'employee' and record.holiday_status_id.name == 'Study Leave' and record.type == 'remove':        
                self.write(cr, uid, ids, {'state':'validate3', 'manager_id': manager})        
            elif record.holiday_type == 'employee' and record.holiday_status_id.name == 'Unpaid Leave' and record.type == 'remove':        
                self.write(cr, uid, ids, {'state':'validate3', 'manager_id': manager})        
            else:    
                self.write(cr, uid, ids, {'state':'validate'})
        return True

    def ceo_validate(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
