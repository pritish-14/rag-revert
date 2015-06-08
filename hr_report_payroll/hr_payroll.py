from openerp.osv import fields, osv

class hr_payslip_line(osv.osv):
    '''
    Payslip Line
    '''

    _inherit = 'hr.payslip.line'
    _columns = {
        'employee_id': fields.related('slip_id','employee_id', type='many2one', relation='hr.employee', string="Employee"),    
        'staff_no': fields.related('employee_id','staff_no', type='integer', string="Staff No"),
        'company_id': fields.related('slip_id','company_id', type='many2one', relation='res.company', string="Company"), 
        'nhif_no': fields.related('employee_id','nhif_no', type='integer', string="NHIF Card Number"),           
        'pin_no': fields.related('employee_id','pin_no', type='integer', string="PIN"),           
        'birthday': fields.related('employee_id','birthday', type='date', string="Date of Birth"), 
	'employment_date': fields.related('employee_id','employment_date', type='date', string="Joining Month"),
	'exit_date': fields.related('employee_id','exit_date', type='date', string="Leaving Month"),
	'employee_month': fields.char('Employee Monthly Contribution'),
	'employer_month': fields.char('Employer Monthly Contribution'),
	'employee_m_date': fields.char('Employee Contribution to Date'),
	'employer_m_date': fields.char('Employer Contribution to Date'),
	'total_date': fields.char('Total Contribution to Date'),
                                 
    }


