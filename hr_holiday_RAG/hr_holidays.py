import datetime 
import math
import time
import calendar
from operator import attrgetter


from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from datetime import date
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta

def last_day_of_month(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)


def first_day_of_month(date):
    return date.replace(day=1)


class holiday_calendar_period(osv.osv):
    _name = "holiday.calendar.period"
    _description = "Holidays Calendar Period"
    _columns = {
        'name': fields.char('Holiday Name', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),
        'holiday_id': fields.many2one('hr.holidays.calendar', 'Holiday'),
    }
    
class allocated_leave_year(osv.osv):
    _inherit = "hr.employee"
    _columns = {
        'allocated_leaves_year': fields.one2many(
            'allocated.leave.year', 'employee_id', 'Allocated leave',
        ),
    }

class AllocatedLeavesYear(osv.osv):
    _name = "allocated.leave.year"
    
    
    def _utilized_leaves(self, cr, uid, ids, utilized_leaves, arg, context=None):
        res={}
        utilized_leaves=0
        year_record = self.browse(cr, uid, ids, context=context)
        month_records = self.pool.get('allocated.leaves.month')
        print year_record
        for years in year_record:
            month_same_year = month_records.search(cr,uid,[('associated_leave_year', '=', years.id)], context=context)
            
            matching_month_record = month_records.browse(cr, uid, month_same_year, context=context)
            for months in matching_month_record:
                utilized_leaves+=float(months.utilized_leaves)     
                res[years.id] = utilized_leaves
        return res
    
    _columns = {
        'year': fields.char('Year'),
        'monthly_leaves': fields.one2many(
            'allocated.leaves.month', 'associated_leave_year', 'Monthly Leaves' 
        ),
        'start_date':fields.date('Start Date'),
        'end_date':fields.date('End date'),
        'allocated_leaves':fields.float('Allocated leaves'),
        'utilized_leaves': fields.function(_utilized_leaves,string='Utilized Leaves'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
    }
    
    
class AllocatedLeavesMonth(osv.osv):
    _name = "allocated.leaves.month"
    
    
    def _pending_leaves(self, cursor, user, ids, field_name, arg, context=None):
        res={}
        months = self.browse(cursor, user, ids, context=context)
        '''
        for month in months:
        
            print "In Pending Leaves"
            print month.allocated_leaves
            print month.carry_over
            print month.utilized_leaves
            pending_leaves = (float(month.allocated_leaves) + month.carry_over) - float(month.utilized_leaves)
            res[month.id]=pending_leaves
        '''
        for index in range(0, len(months)):
            if(index ==0):
                pending_leaves = (float(months[index].allocated_leaves) + months[index].carry_over) - float(months[index].utilized_leaves)
                res[months[0].id]=pending_leaves
                
            else:
                pending_leaves = (float(months[index].allocated_leaves) + months[index-1].pending_leaves) - float(months[index].utilized_leaves) + months[index].carry_over
                res[months[index].id] = pending_leaves
        return res
    '''    
    def _carry_over(self, cursor, user, ids, field_name, arg, context=None):
        res = {}
        months = self.browse(cursor, user, ids, context=context)
        print "Carry Over " ,str(months)
        
       
        # months_id = [month for month in self.browse(cursor, user, ids, context=context)].sort()
        # print months_id
        print ids
        # First month in list will have the smallest id
        # Calculating Carry overs for other months
        for index in range(0, len(months)):
            if(index ==0):
                res[months[0].id]=0
                print months[index]
                
            else:
                print months[index-1].pending_leaves
                res[months[index].id] = months[index-1].pending_leaves
                print "In Carry Over", str(months[index-1].pending_leaves)
        return res
    ''' 
    _columns = {
        'month': fields.selection(
            [
                ('1', 'January'),
                ('2', 'February'),
                ('3', 'March'),
                ('4', 'April'),
                ('5', 'May'),
                ('6', 'June'),
                ('7', 'July'),
                ('8', 'August'),
                ('9', 'September'),
                ('10', 'October'),
                ('11', 'November'),
                ('12', 'December'),
            ], 'Month'),
        'allocated_leaves': fields.char('Allocated Leaves'),
        'utilized_leaves': fields.char('Utilized Leaves'),
        'pending_leaves': fields.function(
            _pending_leaves, string='Pending Leaves', type='float',
            store={
                'allocated.leaves.month': (
                    lambda self, cursor, user, ids, context={}: ids, [
                        'allocated_leaves', 'utilized_leaves'], 10),
            }
        ),
        'carry_over':fields.float('Carry Over'),
        'associated_leave_year': fields.many2one(
            'allocated.leave.year','Associated Leave Year'),
    }
    

class holiday_calendar_year(osv.osv):
    _name = "holiday.calendar.year"
    _description = "Calendar Year"
    _columns = {
        'name': fields.char('Calendar Year', required=True),
        'start_date':fields.date('Start Date'),
        'end_date':fields.date('End Date'),
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'There is already Calendar Year defined for this year!'),
    ]
    
    def onchange_start_date(self, cr, uid, ids, start_date,context=None):
        if start_date:
            start_date=datetime.datetime.strptime(start_date, '%Y-%m-%d')
            start_year = start_date.year
            start_day = start_date.day
            end_date =  start_date+ relativedelta(year=start_year+1)+ relativedelta(day=start_day-1)
            return {'value': {'end_date': end_date}}
    

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
        if context is None:
            context = {}
        if not context.get('employee_id',False):
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee
            return super(hr_holidays_status, self).name_get(cr, uid, ids, context=context)

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if not record.limit:
                name = name + ('  (%g/%g)' % (record.leaves_taken or 0.0, record.max_leaves or 0.0))
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


class hr_holiday(osv.osv):
    _inherit = "hr.holidays"
    _track = {
        'state': {
            'hr_holidays.mt_holidays_approved': lambda self, cr, uid, obj, ctx=None: obj.state == 'validate',
            'hr_holidays.mt_holidays_refused': lambda self, cr, uid, obj, ctx=None: obj.state == 'refuse',
            'hr_holidays.mt_holidays_confirmed': lambda self, cr, uid, obj, ctx=None: obj.state == 'confirm',
        },
    }

   
    
    _check_holidays = lambda self, cr, uid, ids, context=None: self.check_holidays(cr, uid, ids, context=context)
        
    def _get_default_leave(self, cursor, user, ids, context=None):
        res = {}
        if context is None:
            context = {}
        status_id = self.pool.get('hr.holidays.status').search(cursor, user, [('name', '=', 'Annual Leave')])    
        return self.pool.get('hr.holidays.status').browse(cursor, user, status_id)
        
    def _check_date(self, cursor, user, ids, context=None):
        res = super(hr_holiday, self)._check_date(cursor, user, ids, context)
        for holiday in self.browse(cursor, user, ids, context=context):
            if holiday.holiday_status_id.name == "Sick Leave":
                return True
        return res
            

    _check_days = lambda self, cr, uid, ids, context=None: self.check_holidays(cr, uid, ids, context=context)
            
    _columns = {
        'name': fields.char('Description', size=64),
        'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'Waiting Manager Apporval'), ('refuse', 'Refused'), ('validate1', 'Waiting Department Manager Apporval'), ('validate2', 'Waiting HR Manager Apporval'), ('validate3', 'Waiting CEO Apporval'), ('validate', 'Approved')],
            'Status', readonly=True, copy=False,
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.'),
        'attachment_ids': fields.one2many('ir.attachment', 'leave_id', 'Attachments', readonly=True, states={'draft':[('readonly',False)]}),
        'user_id':fields.related('employee_id', 'user_id', type='many2one', relation='res.users', string='User', store=True),
        'date_from': fields.date('Start Date', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, select=True, copy=False),
        'date_to': fields.date('End Date', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, copy=False),
        'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type", required=True,readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'employee_id': fields.many2one('hr.employee', "Employee", select=True, invisible=False, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'manager_id': fields.many2one('hr.employee', 'First Approval', invisible=False, readonly=True, copy=False,
                                      help='This area is automatically filled by the user who validate the leave'),
        'notes': fields.text('Reasons',readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'number_of_days_temp': fields.float('Allocation', readonly=True, required=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, copy=False),
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
        'allocation_to': fields.datetime('End Date', readonly=True, states={'draft':[('readonly',False)]}),
        'calendar_year': fields.many2one('holiday.calendar.year','Year'),        
    }
    _defaults = {
        'state': 'draft',
        'holiday_status_id': _get_default_leave,
    }

    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from','date_to']),
        (_check_days, 'Sorry! You have already taken maximum leaves for this leave type', ['state','number_of_days_temp'])
    ] 

    def write(self, cr, uid, ids, vals, context=None):
        res = super(hr_holiday, self).write(cr, uid, ids, vals, context=context)    
        if vals.get('state') and vals['state'] not in ['confirm','validate1','validate2', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_user'):
            raise osv.except_osv(_('Warning!'), _('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % vals.get('state'))
                    
        return True

    def check_holidays(self, cr, uid, ids, context=None):
    
        HolidayStatus = self.pool.get('hr.holidays.status')
    
        for record in self.browse(cr, uid, ids, context=context):
            print record.employee_id.gender
            print record.holiday_status_id.name
            if record.holiday_status_id.name == 'Paternity Leave':
                if record.employee_id.gender == 'male':
                    leave_days = HolidayStatus.get_days(
                            cr, uid, [record.holiday_status_id.id],
                            record.employee_id.id, context=context
                        )[record.holiday_status_id.id]
                    if (leave_days['leaves_taken'] + record.number_of_days_temp) > 14:                                
                        raise osv.except_osv(
                            _('Warning!'),
                            _('Sorry! You have already taken maximum leaves ' \
                              'for this leave type')
                        )
                    if not record.attachment_ids:
                        raise osv.except_osv(
                            _('Warning!'),
                            _('Birth Notification is mandatory')
                        )
                else:
                    raise osv.except_osv(
                        _('Warning!'),
                        _('Paternity Leave can only be taken by Male ' \
                          'Employees.')
                    )
            elif record.holiday_status_id.name == 'Unpaid Leave':
                leave_days = HolidayStatus.get_days(
                    cr, uid, [record.holiday_status_id.id],
                    record.employee_id.id, context=context
                )[record.holiday_status_id.id]
                
                if (leave_days['leaves_taken'] + record.number_of_days_temp) > 42: 
                    raise osv.except_osv(_('Warning!'),_('Sorry! You have already taken maximum leaves for this leave type'))                    
            elif record.holiday_status_id.name == 'Maternity Leave':
                if record.employee_id.gender == 'female':
                    leave_days = HolidayStatus.get_days(
                        cr, uid, [record.holiday_status_id.id],
                        record.employee_id.id, context=context
                    )[record.holiday_status_id.id]
                    
                    if (leave_days['leaves_taken'] + record.number_of_days_temp) > 92:                                
                        raise osv.except_osv(
                            _('Warning!'),
                            _('Sorry! You have already taken maximum leaves '\
                              'for this leave type')
                          )
                else:
                    raise osv.except_osv(
                        _('Warning!'),
                        _('Paternity Leave can only be taken by Female ' \
                          'Employees.')
                    )
            elif record.holiday_status_id.name == 'Compassionate Leave':
                leave_days = HolidayStatus.get_days(cr, uid, [record.holiday_status_id.id], record.employee_id.id, context=context)[record.holiday_status_id.id]
                if (leave_days['leaves_taken'] + record.number_of_days_temp) > 5:
                    raise osv.except_osv(_('Warning!'),_('Sorry! You have already taken maximum leaves for this leave type'))                    
            elif record.holiday_status_id.name == 'Compulsory Leave':
                leave_days = HolidayStatus.get_days(cr, uid, [record.holiday_status_id.id], record.employee_id.id, context=context)[record.holiday_status_id.id]
                if (leave_days['leaves_taken'] + record.number_of_days_temp) > 30:
                    raise osv.except_osv(_('Warning!'),_('Sorry! You have already taken maximum leaves for this leave type'))                    
            elif record.holiday_status_id.name == 'Study Leave':
                raise osv.except_osv(
                        _('Warning!'),
                        _('Attachment is required')
                    )    
            
        return True

    def holidays_refuse(self, cr, uid, ids, context=None):
        allow_group = []
        coo_group = self.pool.get('ir.model.data').get_object(cr, uid, 'medical_premium', 'group_ceo_apagen')
        coo_users = [user.id for user in coo_group.users]
        allow_group.extend(coo_users)

        man_group = self.pool.get('ir.model.data').get_object(cr, uid, 'base', 'group_hr_manager')
        man_users = [user.id for user in man_group.users]
        allow_group.extend(man_users)
        for record in self.browse(cr, uid, ids):
            if uid != record.employee_id.parent_id.user_id.id and uid not in allow_group:
                raise osv.except_osv(_('Warning!'),_('Only manager of this employee can refuse the leave.'))
        return super(hr_holiday, self).holidays_refuse(cr, uid, ids, context=context)

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

    def _get_number_of_days(self, cr, uid, ids, date_from, date_to, context=None):
        """Returns a float equals to the timedelta between two dates given as string."""
        DATETIME_FORMAT = "%Y-%m-%d"

        date_from = date_from.split(' ')[0]
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        date_to = date_to.split(' ')[0]
        to_date = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
#        to_date = to_dt + datetime.timedelta(hours=23)
        ResourceCal = self.pool.get('resource.calendar')
        calendar_ids = ResourceCal.search(cr, uid, [])
        if not calendar_ids:
            raise osv.except_osv(_('Warning!'),_('Resource Working Calendar is missing. It needs to be created.'))
        hours_start_end = ResourceCal.interval_hours_get(cr, uid, calendar_ids[0], from_dt, to_date)
        cal = ResourceCal.browse(cr, uid, calendar_ids[0])

        # Using resource.calendar, check from date should be a working
        # day. If not, then get the first working day of month.
        
        from_dt = ResourceCal.get_next_day(cr, uid, cal.id, from_dt, context) if from_dt.weekday() not in [calendar_attendance.dayofweek for calendar_attendance in cal.attendance_ids] else from_dt
        
        working_hours_on_day = ResourceCal.working_hours_on_day(cr, uid, cal, from_dt)
        holidays =self.get_holidays_list(cr, uid, ids, from_dt, to_date)
#        if from_dt == to_dt:
#            days = 1
        #else:
        days = hours_start_end / (working_hours_on_day or 9)
        total = days - holidays
        return total

    def onchange_date_from(self, cursor, user, ids, date_to, date_from, holiday_status_id, context=None):
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
            holiday_status = self.pool.get('hr.holidays.status')
            holiday_type = holiday_status.browse(cursor, user, holiday_status_id,context=context)
            print holiday_type.name
            if(holiday_type.name == "Annual Leave" or holiday_type.name == "Unpaid Leave" or holiday_type.name == "Compulsory Leave" ):
                print "ANNUAL LEAVE"
                diff_day = self._get_number_of_days(cursor, user, ids, date_from, date_to)
                result['value']['number_of_days_temp'] = round(math.floor(diff_day))
                result['value']['number_of_days_temp1'] = round(math.floor(diff_day))
            else:
                date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")
                date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
                days_diff = (date_to - date_from)
                print ">>>>",str(days_diff)
                no_of_days_diff = days_diff.days + 1
                print ">>>>",str(no_of_days_diff)
                result['value']['number_of_days_temp'] = no_of_days_diff
                result['value']['number_of_days_temp1'] = no_of_days_diff              
        else:
            result['value']['number_of_days_temp'] = 0
            result['value']['number_of_days_temp1'] = 0

        return result

    def onchange_date_to(self, cursor, user, ids, date_to, date_from, holiday_status_id, context=None):
        """
        Update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # Compute and update the number of days
        
        if (date_to and date_from) and (date_from <= date_to):
            holiday_status = self.pool.get('hr.holidays.status')
            holiday_type = holiday_status.browse(cursor, user, holiday_status_id,context=context)
            print holiday_type.name
            if(holiday_type.name == "Annual Leave" or holiday_type.name == "Unpaid Leave" or holiday_type.name == "Compulsory Leave" ):
                print "ANNUAL LEAVE"
                diff_day = self._get_number_of_days(cursor, user, ids, date_from, date_to)
                result['value']['number_of_days_temp'] = round(math.floor(diff_day))
                result['value']['number_of_days_temp1'] = round(math.floor(diff_day))
            else:
                date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")
                date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
                days_diff = (date_to - date_from)
                print ">>>>",str(days_diff)
                no_of_days_diff = days_diff.days +1
                print ">>>>",str(no_of_days_diff)
                result['value']['number_of_days_temp'] = no_of_days_diff
                result['value']['number_of_days_temp1'] = no_of_days_diff
        else:
            result['value']['number_of_days_temp'] = 0
            result['value']['number_of_days_temp1'] = 0

        return result

    def holidays_confirm(self, cursor, user, ids, context=None):
        if context is None: context = {}
        holi_status_obj = self.pool.get('hr.holidays.status')
        for record in self.browse(cursor, user, ids):
            if not record.employee_id and record.employee_id.parent_id:
                raise osv.except_osv(_('Warning!'),_('Please assign manager of this employee in Employee form.'))
            if not record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                raise osv.except_osv(_('Warning!'),_('Please assign user in this employee manager.'))

            if record.type=='remove':
                sequence = self.pool.get('ir.sequence').get(cursor, user, 'hr.holidays.lreq') or ''
            elif record.type=='add':
                sequence = self.pool.get('ir.sequence').get(cursor, user, 'hr.holidays.areq') or ''

            if record.holiday_type == 'employee' and record.holiday_status_id.name == 'Compassionate Leave' and record.type == 'remove':
                if not record.notes and not record.relative:
                    raise osv.except_osv(_('Warning!'),_('You have to add reason as notes and chose relative in .'))                                                      
            elif record.holiday_type == 'employee' and record.holiday_status_id.name == 'Maternity Leave' and record.type == 'remove' and record.employee_id.gender == 'male':
                raise osv.except_osv(_('Warning!'),_('Maternity Leaves are allowed to Females only.'))
                
            elif record.holiday_type == 'employee' and record.holiday_status_id.name == 'Paternity Leave' and record.type == 'remove' and record.employee_id.gender == 'female':
                raise osv.except_osv(_('Warning!'),_('Paternity Leaves are allowed to Males only.'))
                
            elif record.holiday_type == 'employee' and record.holiday_status_id.name == 'Study Leave' and record.type == 'remove':
                if not record.attachment_ids:
                    raise osv.except_osv(_('Warning!'),_('You have to add atleast one attachment for Study Leave detail.'))
            elif record.holiday_type == 'employee' and record.holiday_status_id.name == 'Sick Leave' and record.type == 'remove':
                if not record.attachment_ids:
                    raise osv.except_osv(
                        _('Warning!'),
                        _('You have to attach atleast one supporting ' \
                          'document for Sick Leave request.')
                    )
                sick_allocated_year = 0
                print record.holiday_status_id.id
                print record.date_from
                
                # Get the calendar year based on leave dates
                calendar_year = self.pool.get('holiday.calendar.year')
                requesting_year = calendar_year.search(cursor, user, [
                                    ('start_date', '<=',record.date_from),
                                    ('end_date','>=',record.date_to),
                                ],context=context, limit=1,
                )
                if requesting_year:
                    requesting_year_dates = calendar_year.browse(cursor, user, requesting_year, context=context)
                
                    sick_leave_record_ids =self.search(cursor, user, [
                                        ('state', '=','validate'),
                                        ('employee_id','=',record.employee_id.id),
                                        ('date_from','>=',requesting_year_dates.start_date),
                                        ('date_to','<=',requesting_year_dates.end_date),
                                        ('holiday_status_id','=',record.holiday_status_id.id)
                                    ],context=context
                    )
                    for sick_leave_record_id in  sick_leave_record_ids:
                        print sick_leave_record_id
                        if (sick_leave_record_id):
                                sick_leaves = self.browse(cursor, user, sick_leave_record_id, context=context)
                                sick_allocated_year += sick_leaves.number_of_days_temp
                    print "--->",str(sick_allocated_year)
                    sick_leaves_left = 45 - sick_allocated_year
                    print "--->",str(sick_leaves_left)
                    if( record.number_of_days_temp > sick_leaves_left):
                        raise osv.except_osv(_('Warning!'),_("You are left only with '%s' sick leaves!") % (sick_leaves_left))
                        
            if record.type=='remove':         
                self.write(cursor, user, [record.id], {'state': 'confirm'})
            elif record.type=='add':                
                self.write(cursor, user, [record.id], {'state': 'validate'})            
        return True

    def holidays_approve(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id], context=context)
        return self.write(cr, uid, ids, {'state': 'validate3'})

    def allocation_approve(self, cr, uid, ids, context=None):
        Employee = self.pool.get('hr.employee')
        allocated_leave_obj = self.pool.get('allocated.leave.year')
        allocated_leave_month =self.pool.get('allocated.leaves.month')
        for record in self.browse(cr, uid, ids, context=context):
            emp_record = record.employee_id.id
            if not record.calendar_year:
                raise osv.except_osv('Error!', 'Select Year')
                return False
            start_date = record.calendar_year.start_date
            end_date = record.calendar_year.end_date

            if record.holiday_type == "employee":
                val = {
                    'year': record.calendar_year.name,
                    'allocated_leaves': record.number_of_days_temp,
                    'start_date': start_date,
                    'end_date': end_date,
                    'employee_id':emp_record,
                }
                    
                id_allocated_leave_obj = allocated_leave_obj.create(cr, uid, 
                                                                    val, 
                                                                    context=context)
                start_month = datetime.datetime.strptime(start_date, '%Y-%m-%d').month
                count=0
                for i in range(1,13):
                    vals = {
                            'month': str(start_month),
                            'allocated_leaves': (record.number_of_days_temp)/12,
                            'associated_leave_year':id_allocated_leave_obj,
                    }
                    if start_month<12:
                        start_month=start_month+1
                    else:
                        start_month =1
                        start_month+=count
                        count=count+1
                        
                    
                    allocated_leave_month.create(cr, uid, vals, context=context)
                    
        if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
            self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id], context=context)
        return self.write(cr, uid, ids, {'state': 'validate'})
                    
            
            

    def holidays_approval(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, uid, [record.id], {'manager_id': manager})
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('calendar.event')
                meeting_vals = {
                    'name': record.name or _('Leave Request'),
                    'categ_ids': record.holiday_status_id.categ_id and [(6,0,[record.holiday_status_id.categ_id.id])] or [],
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'start': record.date_from,
                    'stop': record.date_to,
                    'allday': False,
                    'state': 'open',            # to block that meeting date in the calendar
                    'class': 'confidential'
                }   
                #Add the partner_id (if exist) as an attendee             
                if record.user_id and record.user_id.partner_id:
                    meeting_vals['partner_ids'] = [(4,record.user_id.partner_id.id)]
                    
                ctx_no_email = dict(context or {}, no_email=True)
                meeting_id = meeting_obj.create(cr, uid, meeting_vals, context=ctx_no_email)
                self._create_resource_leave(cr, uid, [record], context=context)
                self.write(cr, uid, ids, {'meeting_id': meeting_id})
            elif record.holiday_type == 'category':
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
        return self.write(cr, uid, ids, {'state': 'validate'})
        
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
        self.write(cr, uid, ids, {'state':'validate2'})                        
        return True
        
    ''' Method to search record on basis of month and browse pending leaves '''    
    def month_search_browse(self, cursor, user, ids, allocated_leaves_year, LeavesMonth, month, context):
        print allocated_leaves_year
        print month
        print LeavesMonth
        
        month_rec = LeavesMonth.search(
            cursor, user,[
                ('associated_leave_year', 'in', allocated_leaves_year),
                ('month', '=', month)
            ], context=context
        )
        print month_rec
        
        pending_leaves_for_month = LeavesMonth.browse(
                cursor, user, month_rec, context=context
            ).pending_leaves
        print pending_leaves_for_month
            
        return pending_leaves_for_month

    def holidays_validate(self, cursor, user, ids, context=None):
        '''
        To update the utilized leaves in employee record after final approval
        '''
        Employee = self.pool.get('hr.employee')
        LeavesMonth= self.pool.get('allocated.leaves.month')
        LeavesYear= self.pool.get('allocated.leave.year')
        leave_request = self.browse(cursor, user, ids)
        if (leave_request.holiday_status_id.name == "Annual Leave"):
            no_of_days_requested = leave_request.number_of_days_temp
            employee_record = leave_request.employee_id

            start_date = datetime.datetime.strptime(leave_request.date_from, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(leave_request.date_to, '%Y-%m-%d')
            
            start_month = start_date.month
            end_month = end_date.month
            
            start_day = start_date.day
            end_day = end_date.day
            
            start_year = start_date.year
            allocated_leaves_year = LeavesYear.search(
                cursor, user,[
                    ('employee_id', '=', employee_record.id),
                    ('start_date','<=',start_date),
                    ('end_date','>=',end_date)
                    ],
                context=context
            )
            
            print allocated_leaves_year
            if (len(allocated_leaves_year) ==0):
                raise osv.except_osv(
                            'No matching Year Found'
                        )
            if(len(allocated_leaves_year)>1):
                raise osv.except_osv(
                            'Duplicate Years exist'
                        )
                
            start_month_pending_leaves = self.month_search_browse(cursor, user, ids, allocated_leaves_year,LeavesMonth,start_month,context)
            print start_month_pending_leaves
            
            current_date = datetime.datetime.now()
            current_month = current_date.month
            if(current_month != start_month):
                raise osv.except_osv(
                            'Leaves can be requested only for the present month'
                        )
            else:
                if (start_month==end_month):
                    if start_month_pending_leaves < no_of_days_requested:
                        raise osv.except_osv(
                            'No Leaved Allowed',
                            'Leaves for this month have been utilized. You are not' \
                            ' allowed to take the leave for this month'
                        )
                    vals = {
                        'utilized_leaves':no_of_days_requested
                    }
                    month_leave_records = LeavesMonth.search(
                    cursor, user,[
                        ('associated_leave_year', 'in', allocated_leaves_year),
                        ('month', '=', start_month)
                    ], context=context
                    )
                    
                    LeavesMonth.write(cursor, user, month_leave_records, vals)
                else:
                
                    raise osv.except_osv(
                            'Leaves are allowed only for the same month'
                        )   
      
        ids2 = Employee.search(cursor, user, [('user_id', '=', user)])
        manager = ids2 and ids2[0] or False
        for record in leave_request:
            if record.holiday_type == 'employee' and record.holiday_status_id.name == 'Study Leave' and record.type == 'remove':        
                self.write(cursor, user, ids, {'state':'validate3', 'manager_id': manager})        
            elif record.holiday_type == 'employee' and record.holiday_status_id.name == 'Unpaid Leave' and record.type == 'remove':        
                self.write(cursor, user, ids, {'state':'validate3', 'manager_id': manager})        
            else:    
                self.write(cursor, user, ids, {'state':'validate'})
        return True

    def ceo_validate(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        return True

    def calculate_carryover(self, cursor, user, automatic=False, date=False, context=None):
        '''Method to calculate the carryover leaves for the month of 
        current date
        '''
        emp_obj = self.pool.get('hr.employee')
        month_obj = self.pool.get('allocated.leaves.month')
        year_obj = self.pool.get('allocated.leave.year')

        active_emp = emp_obj.search(cursor, user, [('active','=',True)])
        emp_records = emp_obj.browse(cursor, user, active_emp, context=context)

        if not date:
            current_date = datetime.datetime.now()
            current_month = current_date.month
        
        for employee in emp_records:
            allocation_year = year_obj.search(
                cursor, user, [
                    ('start_date', '<=', str(current_date.date())),
                    ('end_date', '>=', str(current_date.date())),
                    ('employee_id', '=', employee.id)
                ], context=context
            )
            if allocation_year:
                if len(allocation_year) > 1:
                    raise osv.except_osv('Error !', 'Some error with Employee ' \
                    'Data. Contact Administrator')

                months_list = month_obj.search(
                    cursor, user, [
                        ('month', '=', current_month),
                        ('associated_leave_year', '=', allocation_year[0]),
                    ]
                )

                if len(months_list) > 1:
                    raise osv.except_osv('Error !', 'Some error with Employee ' \
                    'Data on Months. Contact Administrator')
                
                if(current_month == 1):
                    pre_month = month_obj.search(
                        cursor, user, [
                            ('month', '=', 12),
                            ('associated_leave_year', '=', allocation_year[0]),
                        ]
                    )
                else:
                    pre_month = month_obj.search(
                        cursor, user, [
                            ('month', '=', current_month-1),
                            ('associated_leave_year', '=', allocation_year[0]),
                        ]
                    )
                pre_month_record = month_obj.browse(
                    cursor, user, pre_month, context=context
                )
                year_record = year_obj.browse(cursor, user, allocation_year)
                year_start_date =  year_record.start_date
                year_start_month = datetime.datetime.strptime(year_start_date, '%Y-%m-%d').month

                if(current_month== year_start_month):
                    carry_overs = 0
                else:
                    carry_overs = pre_month_record.pending_leaves

                month_obj.write(cursor, user, months_list, {'carry_over': carry_overs}, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
