# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import osv
from datetime import datetime, timedelta
import time
from openerp.tools.translate import _
from openerp import netsvc

class wizard_leave_check(osv.osv_memory):
    _name = "wizard.leave.check"
    _description = "Leave check"

    def proceed(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        holiday_obj = self.pool.get('hr.holidays')
        holi_status_obj = self.pool.get('hr.holidays.status')
        sick_leave_count = context.get('sick_leave_count')
        remaining_sick_leave = context.get('remaining_sick_leave')
        resource_pool = self.pool.get('resource.resource')
        cal_pool = self.pool.get('resource.calendar')
        if context.get('active_id') and context.get('employee_id'):
            annual_status_id = holi_status_obj.search(cr, uid, [('name', '=', 'Annual Leave')])
            if annual_status_id:
                leaves_rest_annaul = holi_status_obj.get_days( cr, uid, [annual_status_id[0]], context['employee_id'], False)[annual_status_id[0]]['remaining_leaves']
                if not leaves_rest_annaul:
                    raise osv.except_osv(_('Warning!'),_('You cannot apply for leave as Annual Leave is also exhausted.'))
                if sick_leave_count > leaves_rest_annaul:
                    raise osv.except_osv(_('Warning!'),_('You cannot apply for sick leave as you have only %s days Annual Leaves remain. Instead apply for lesser number of leaves') %leaves_rest_annaul)
                if remaining_sick_leave and remaining_sick_leave < sick_leave_count:
                    holiday =  holiday_obj.browse(cr, uid, context['active_id'])
                    resource_ids = resource_pool.search(cr, uid, [('user_id', '=', holiday.employee_id.user_id.id)])
                    calendar = resource_pool.browse(cr, uid, resource_ids[0]).calendar_id
                    calendar_id = calendar.id
                    date_from = datetime.strptime(holiday.date_from,'%Y-%m-%d %H:%M:%S')
                    working_hour_per_day = cal_pool.working_hours_on_day(cr, uid, calendar, date_from)
                    leave_interval = cal_pool.interval_get(cr, uid, calendar_id, date_from, sick_leave_count * working_hour_per_day)
                    sick_leave_range = []
                    annual_leave_range = []
                    if leave_interval:
                        for i in range(0, remaining_sick_leave):
                            sick_leave_range.append(leave_interval[i])
                        for j in range(remaining_sick_leave, sick_leave_count):
                            annual_leave_range.append(leave_interval[j])
                        if sick_leave_range:
                            sick_leave_from = sick_leave_range[0][0].strftime('%Y-%m-%d %H:%M:%S')
                            sick_leave_to = sick_leave_range[-1][1].strftime('%Y-%m-%d %H:%M:%S')
                            holiday_obj.write(cr, uid, [context['active_id']],
                                      {'number_of_days_temp': remaining_sick_leave,
                                       'date_from': sick_leave_from,
                                       'date_to': sick_leave_to})
                        if annual_leave_range:
                            annual_leave_from = annual_leave_range[0][0].strftime('%Y-%m-%d %H:%M:%S')
                            annual_leave_to = annual_leave_range[-1][1].strftime('%Y-%m-%d %H:%M:%S')
                            annual_leave_id = holiday_obj.create(cr, uid,
                                      {'name': 'Annual Leave consumption based on Sick Leave',
                                       'number_of_days_temp': sick_leave_count - remaining_sick_leave,
                                       'holiday_status_id': annual_status_id[0],
                                       'employee_id': context['employee_id'],
                                       'date_from': annual_leave_from,
                                       'date_to': annual_leave_to})
                            wf_service.trg_validate(uid, 'hr.holidays', annual_leave_id, 'submit', cr)
                    return True
                holiday_obj.write(cr, uid, [context['active_id']], {'holiday_status_id': annual_status_id[0]})
                return True
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        holiday_obj = self.pool.get('hr.holidays')
        wf_service.trg_validate(uid, 'hr.holidays', context['active_id'], 'reset', cr)
        holiday_obj.write(cr, uid, [context['active_id']], {'state': 'draft'}, context=context)
        return {'type': 'ir.actions.act_window_close'}