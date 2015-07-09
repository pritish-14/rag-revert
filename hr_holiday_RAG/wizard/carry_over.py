from openerp.osv import fields, osv
import datetime


class CarryOver(osv.osv):
    _name = "cal.carryovers"
    
    def yes(self, cursor, user, ids, context=None):
    
        emp_obj = self.pool.get('hr.employee')
        month_obj = self.pool.get('allocated.leaves.month')
        year_obj = self.pool.get('allocated.leave.year')

        active_emp = emp_obj.search(cursor, user, [('active','=',True)])
        emp_records = emp_obj.browse(cursor, user, active_emp, context=context)

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
            print "Allocation Year " , str(allocation_year)
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
                
                month = month_obj.browse(
                    cursor, user, months_list[0], context=context
                )
                if(current_month == 12):
                    pre_month = month_obj.search(
                        cursor, user, [
                            ('month', '=', 1),
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
                carry_overs = pre_month_record.pending_leaves
                print carry_overs
                print pre_month_record
                print allocation_year
                month_obj.write(cursor, user, month.id, {'carry_over': carry_overs}, context=context)
    
