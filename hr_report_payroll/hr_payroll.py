
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval

class hr_payslip_line(osv.osv):
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
                                 
        'total': fields.function(_calculate_total, method=True, type='float', string='Amount', digits_compute=dp.get_precision('Payroll'),store=True ),
        'employee_id': fields.related('slip_id', 'employee_id', type='many2one', relation='hr.employee', string="Employee"),    
        'staff_no': fields.related('employee_id', 'staff_no', type='integer', string="Staff No"),
        'company_id': fields.related('slip_id', 'company_id', type='many2one', relation='res.company', string="Company"), 
        'nhif_no': fields.related('employee_id','nhif_no', type='integer', string="NHIF Card Number"),           
        'pin_no': fields.related('employee_id', 'pin_no', type='integer', string="PIN"),           
        'birthday': fields.related('employee_id', 'birthday', type='date', string="Date of Birth"),                           
    }
    
class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread', 'ir.needaction_mixin']    

    def _cal_total_days(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'total_days' : 0.0
            }
            val4 = 0.0
            for line in order.worked_days_line_ids:
                total_day = line.number_of_days
                val4 = val4 + total_day
            res[order.id] = val4
            print "res[order.id]", res[order.id]
        return res
    
    _columns = {
        'total_days': fields.function(_cal_total_days, string='Total Days', type='float', store=False),   
        'user_id': fields.many2one('res.users', 'Responsible'),
    }        
    
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, pool, cr, uid, employee_id, dict):
                self.pool = pool
                self.cr = cr
                self.uid = uid
                self.employee_id = employee_id
                self.dict = dict

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(amount) as sum\
                            FROM hr_payslip as hp, hr_payslip_input as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()[0]
                return res or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
                            FROM hr_payslip as hp, hr_payslip_worked_days as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done'\
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                return self.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
                            FROM hr_payslip as hp, hr_payslip_line as pl \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
                            (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()
                return res and res[0] or 0.0

        #we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules = {}
        categories_dict = {}
        blacklist = []
        payslip_obj = self.pool.get('hr.payslip')
        inputs_obj = self.pool.get('hr.payslip.worked_days')
        obj_rule = self.pool.get('hr.salary.rule')
        payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
        worked_days = {}
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days[worked_days_line.code] = worked_days_line
        inputs = {}
        for input_line in payslip.input_line_ids:
            inputs[input_line.code] = input_line

        categories_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, categories_dict)
        input_obj = InputLine(self.pool, cr, uid, payslip.employee_id.id, inputs)
        worked_days_obj = WorkedDays(self.pool, cr, uid, payslip.employee_id.id, worked_days)
        payslip_obj = Payslips(self.pool, cr, uid, payslip.employee_id.id, payslip)
        rules_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, rules)

        baselocaldict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj}
        #get the ids of the structures on the contracts and their parent id as well
        structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
        #get the rules of the structure and thier children
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in obj_rule.browse(cr, uid, sorted_rule_ids, context=context):
                key = rule.code + '-' + str(contract.id)
                print "rule.name", rule.name
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                #check if the rule can be applied
                if obj_rule.satisfy_condition(cr, uid, rule.id, localdict, context=context) and rule.id not in blacklist:
                    #compute the amount of the rule
                    if rule.name == "PAYE":
                        rule_id = obj_rule.search(cr, uid, [('name','=','Gross')])                
                        amount, qty, rate = obj_rule.compute_rule(cr, uid, rule_id, localdict, context=context)
                        #check if there is already a rule computed with that code
                        previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                        #set/overwrite the amount computed for this rule in the localdict
                        tot_rule = (amount * qty * rate / 100.0) - 200
                        print "total_rule", tot_rule
                        if tot_rule >= 1 and tot_rule <=10164:
                            tot_rule = tot_rule * 0.10
                        elif tot_rule >= 10165 and tot_rule <=19740:                             
                            tot_rule = tot_rule * 0.15
                        elif tot_rule >= 19741 and tot_rule <=29316:                             
                            tot_rule = tot_rule * 0.20
                        elif tot_rule >= 29317 and tot_rule <=38892:                             
                            tot_rule = tot_rule * 0.25
                        elif tot_rule >= 38893:                             
                            tot_rule = tot_rule * 0.30
                        localdict[rule.code] = tot_rule
                        print "localdict[rule.code]", localdict[rule.code]
                        rules[rule.code] = rule
                        #sum the amount for its salary category
                        localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                        #create/overwrite the rule in the temporary results
                        result_dict[key] = {
                            'salary_rule_id': rule.id,
                            'contract_id': contract.id,
                            'name': rule.name,
                            'code': rule.code,
                            'category_id': rule.category_id.id,
                            'sequence': rule.sequence,
                            'appears_on_payslip': rule.appears_on_payslip,
                            'condition_select': rule.condition_select,
                            'condition_python': rule.condition_python,
                            'condition_range': rule.condition_range,
                            'condition_range_min': rule.condition_range_min,
                            'condition_range_max': rule.condition_range_max,
                            'amount_select': rule.amount_select,
                            'amount_fix': rule.amount_fix,
                            'amount_python_compute': rule.amount_python_compute,
                            'amount_percentage': rule.amount_percentage,
                            'amount_percentage_base': rule.amount_percentage_base,
                            'register_id': rule.register_id.id,
                            'amount': tot_rule - 1162,
                            'employee_id': contract.employee_id.id,
                            'quantity': qty,
                            'rate': rate,
                        }
                    else:
                        #compute the amount of the rule
                        amount, qty, rate = obj_rule.compute_rule(cr, uid, rule.id, localdict, context=context)
                        #check if there is already a rule computed with that code
                        previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                        #set/overwrite the amount computed for this rule in the localdict
                        tot_rule = amount * qty * rate / 100.0
                        print "tot_rule", tot_rule
                        localdict[rule.code] = tot_rule
                        rules[rule.code] = rule
                        #sum the amount for its salary category
                        localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                        #create/overwrite the rule in the temporary results
                        result_dict[key] = {
                            'salary_rule_id': rule.id,
                            'contract_id': contract.id,
                            'name': rule.name,
                            'code': rule.code,
                            'category_id': rule.category_id.id,
                            'sequence': rule.sequence,
                            'appears_on_payslip': rule.appears_on_payslip,
                            'condition_select': rule.condition_select,
                            'condition_python': rule.condition_python,
                            'condition_range': rule.condition_range,
                            'condition_range_min': rule.condition_range_min,
                            'condition_range_max': rule.condition_range_max,
                            'amount_select': rule.amount_select,
                            'amount_fix': rule.amount_fix,
                            'amount_python_compute': rule.amount_python_compute,
                            'amount_percentage': rule.amount_percentage,
                            'amount_percentage_base': rule.amount_percentage_base,
                            'register_id': rule.register_id.id,
                            'amount': amount,
                            'employee_id': contract.employee_id.id,
                            'quantity': qty,
                            'rate': rate,
                        }
                else:
                    #blacklist this rule and its children
                    blacklist += [id for id, seq in self.pool.get('hr.salary.rule')._recursive_search_of_rules(cr, uid, [rule], context=context)]
                
        result = [value for code, value in result_dict.items()]
        return result
    
    def process_sheet(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'email_template_hr_payslip')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'hr.payslip',
        #    'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return self.write(cr, uid, ids, {'paid': True, 'state': 'done'}, ctx)
    
    def send_payslip_email(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        #res = super(payslip, self).send_payslip_email(cr, uid, ids, context)
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'hr_report_payroll', 'email_template_hr_payslip')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        print ctx
        print template_id        
        ctx.update({
            'default_model': 'hr.payslip',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return True

class hr_contract(osv.osv):

    _name = 'hr.contract'
    _inherit = 'hr.contract'

    def _hourly(self, cr, uid, ids, field_name, args, context=None):

        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            rate = 0.0
            if contract.wage_type == 'hourly':
                rate = contract.wage
            elif contract.wage_type == 'daily':
                rate = contract.wage / 8.0
            elif contract.wage_type == 'salary':
                rate = contract.wage / 26.0 / 8.0
            res[contract.id] = rate
        return res

    def _daily(self, cr, uid, ids, field_name, args, context=None):

        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            rate = 0.0
            if contract.wage_type == 'hourly':
                rate = contract.wage * 8.0
            elif contract.wage_type == 'daily':
                rate = contract.wage
            elif contract.wage_type == 'salary':
                rate = contract.wage / 26.0
            res[contract.id] = rate
        return res

    def _monthly(self, cr, uid, ids, field_name, args, context=None):

        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            rate = 0.0
            if contract.wage_type == 'hourly':
                rate = contract.wage * 8.0 * 26.0
            elif contract.wage_type == 'daily':
                rate = contract.wage * 26
            elif contract.wage_type == 'salary':
                rate = contract.wage
            res[contract.id] = rate
        return res

    _columns = {
        'wage_type': fields.selection((('hourly', 'Hourly'),
                                       ('daily', 'Daily'),
                                       ('salary', 'Salary')),
                                      'Wage Type', required=True),
        'wage_hourly': fields.function(_hourly, type='float', digits_compute=dp.get_precision('Intermediate Payroll'), string='Hourly Wages'),
        'wage_daily': fields.function(_daily, type='float', digits_compute=dp.get_precision('Intermediate Payroll'), string='Daily Wages'),
        'wage_monthly': fields.function(_monthly, type='float', digits_compute=dp.get_precision('Intermediate Payroll'), string='Monthly Wages'),
    }

    _defaults = {
        'wage_type': 'salary',
    }

