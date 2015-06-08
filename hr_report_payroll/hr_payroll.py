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
    }
