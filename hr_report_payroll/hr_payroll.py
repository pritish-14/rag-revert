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
    }

class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread', 'ir.needaction_mixin']
    
    def send_payslip_email(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'email_template_send_emp_payslip')[1]
        except ValueError:
            template_id = False

        for data in self.browse(cr, uid, ids, context=context):
            if not data.employee_id.work_email:
            	continue
#                raise osv.except_osv(_('Error!'), _('Please define email for this employee'))

            if not data.contact.work_email:
                raise osv.except_osv(_('Error!'), _('Please define email for this contact'))

            self.pool.get('email.template').send_mail(cr, uid, template_id, data.id, force_send=True, context=context)
        return True


    def ssend_mail(self, cr, uid, ids, context=None):
        email_template_obj = self.pool.get('email.template')
        template_ids = email_template_obj.search(cr, uid, [('model_id.model', '=','hr.payslip')], context=context)
        if template_ids:
              values = email_template_obj.generate_email(cr, uid, template_ids[0], ids, context=context)
              values['subject'] = subject
              values['email_to'] = email_to
              values['body_html'] = body_html
              values['body'] = body_html
              values['res_id'] = False
              mail_mail_obj = self.pool.get('mail.mail')
              msg_id = mail_mail_obj.create(cr, uid, values, context=context)
              if msg_id:
                    mail_mail_obj.send(cr, uid, [msg_id], context=context)
        return True
    
