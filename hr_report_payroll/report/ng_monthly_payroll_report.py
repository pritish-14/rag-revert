#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.report import report_sxw
from openerp.tools import amount_to_text_en
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class hr_monthly_payroll_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(hr_monthly_payroll_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_payslip_rules': self.get_payslip_rules,
            'get_payslip_total': self.get_payslip_total,
            'get_department_name': self.get_department_name,
        })

    def get_payslip_rules(self, obj):
        rules = ['Employee', 'Basic', 'Housing Allowance', 'Transport Allowance', 'Utility Allowance',
                    'Entertainment Allowance', 'Leave Allowance', 'Overtime', 'Bonus','Other Income',
                    'Total Income', 'Pension', 'Paye', 'Lateness Panalty', 'Other Deductions',
                    'Total Deductions', 'Net Salary']
        res = []
        dept_pool = self.pool.get('hr.department')
        emp_pool = self.pool.get('hr.employee')
        payslip_pool = self.pool.get('hr.payslip')
        dept_ids = [x.id for x in obj[0].department_ids]
        emp_ids = emp_pool.search(self.cr, self.uid, [('department_id', 'in', dept_ids)])
        slip_ids = payslip_pool.search(self.cr, self.uid, [('employee_id', 'in', emp_ids)])
        for slip in payslip_pool.browse(self.cr, self.uid, slip_ids):
            from_date = datetime.strptime(slip.date_from, '%Y-%m-%d').strftime('%B')
            to_date = datetime.strptime(slip.date_to, '%Y-%m-%d').strftime('%B')
            if from_date == obj[0].month or to_date == obj[0].month:
                data = dict.fromkeys(rules, '0.0')
                data.update({
                    'Employee': slip.employee_id.name + ' ' + slip.employee_id.surname,
                    })
                for line in slip.line_ids:
                    if line.name in (rules):
                        data.update({line.name: line.total})
                res.append(data)
        return res

    def get_payslip_total(self, obj):
        res = self.get_payslip_rules(obj)
        rules = ['Basic', 'Housing Allowance', 'Transport Allowance', 'Utility Allowance',
                    'Entertainment Allowance', 'Leave Allowance', 'Overtime', 'Bonus','Other Income',
                    'Total Income', 'Pension', 'Paye', 'Lateness Panalty', 'Other Deductions',
                    'Total Deductions', 'Net Salary']
        total = dict.fromkeys(rules, 0.0)
        for rule in rules:
            for r in res:
                total[rule] += float(r.get(rule, 0.0))
        return [total]

    def get_department_name(self, obj):
        dname = []
        if obj and obj[0].department_ids:
            for dept in obj[0].department_ids:
                dname.append(dept.name)
        return ', '.join(dname)

report_sxw.report_sxw('report.ng.payroll.monthly', 'hr.payslip.monthly.payroll', 'addons/hr_report_payroll/report/ng_payroll_monthly_report.rml', parser=hr_monthly_payroll_report, header=False)
