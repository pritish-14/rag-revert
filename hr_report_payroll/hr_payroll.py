from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class hr_payslip_line(osv.osv):
    '''
    Payslip Line
    '''

    _inherit = 'hr.payslip.line'

    def _calculate_total(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = float(line.quantity) * line.amount * line.rate / 100
        return res
    
    _columns = {
        'employee_id': fields.related('slip_id','employee_id', type='many2one', relation='hr.employee', string="Employee"),    
        'staff_no': fields.related('employee_id','staff_no', type='integer', string="Staff No"),
        'company_id': fields.related('slip_id','company_id', type='many2one', relation='res.company', string="Company"), 
<<<<<<< HEAD
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
                                 
=======
        'total': fields.function(_calculate_total, method=True, type='float', string='Amount', digits_compute=dp.get_precision('Payroll'),store=True ),
        'employee_id': fields.related('slip_id', 'employee_id', type='many2one', relation='hr.employee', string="Employee"),    
        'staff_no': fields.related('employee_id', 'staff_no', type='integer', string="Staff No"),
        'company_id': fields.related('slip_id', 'company_id', type='many2one', relation='res.company', string="Company"), 
        'nhif_no': fields.related('employee_id','nhif_no', type='integer', string="NHIF Card Number"),           
        'pin_no': fields.related('employee_id', 'pin_no', type='integer', string="PIN"),           
        'birthday': fields.related('employee_id', 'birthday', type='date', string="Date of Birth"),                           
    }
    
class hr_contract(osv.osv):
    _name = 'hr.contract'
    _description = 'Contract'
    _inherit = ['mail.thread', 'hr.contract', 'ir.needaction_mixin']
    _columns = {
        'wage': fields.float('Basic Salary', digits=(16,2), required=True, help="Basic Salary of the employee"),    
        'mobile_alw': fields.float('Mobile Allowance', digits=(16,2)),        
        'fuel_alw': fields.float('Fuel Allowance', digits=(16,2)),
        'travel_alw': fields.float('Travel Allowance', digits=(16,2)),        
        'icea_deduct': fields.float('ICEA', digits=(16,2)),        
        'insurance_deduct': fields.float('Insurance Deductions', digits=(16,2)),                                        
        'stanbic_loan_deduct': fields.float('Stanbic Loan Deductions', digits=(16,2)),                
        'qway_sacco': fields.float('Q/Way Sacco', digits=(16,2)),        
        'aar_deduct': fields.float('AAR Deduction', digits=(16,2)),        
        'icea_endowment': fields.float('ICEA Endowment', digits=(16,2)),        
        'nation_sacco': fields.float('Nation Sacco', digits=(16,2)),                                        
>>>>>>> ba82df1d09afd9cc6da0a6fcdc8bf06088e948a9
    }


