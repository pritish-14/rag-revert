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
        'total': fields.function(_calculate_total, method=True, type='float', string='Amount', digits_compute=dp.get_precision('Payroll'),store=True ),
        'employee_id': fields.related('slip_id', 'employee_id', type='many2one', relation='hr.employee', string="Employee"),    
        'staff_no': fields.related('employee_id', 'staff_no', type='integer', string="Staff No"),
        'company_id': fields.related('slip_id', 'company_id', type='many2one', relation='res.company', string="Company"), 
        'nhif_no': fields.related('employee_id','nhif_no', type='integer', string="NHIF Card Number"),           
        'pin_no': fields.related('employee_id', 'pin_no', type='integer', string="PIN"),           
        'birthday': fields.related('employee_id', 'birthday', type='date', string="Date of Birth"),                           
    }
