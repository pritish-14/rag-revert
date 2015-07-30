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

class hr_payslip_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(hr_payslip_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_payslip_lines': self.get_payslip_lines,
            'get_payslip_rule': self.get_payslip_rule,
            'get_payslip_deductions': self.get_payslip_deductions,
        })

    def get_payslip_lines(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
        rules = ['LEA', 'OT', 'RD', 'SA', 'ARR', 'BON']
        excludes = ['PEN', 'PAYE', 'LP', 'SAV', 'EL', 'OD', 'TI', 'TD', 'Net']
        for id in range(len(obj)):
            if obj[id].appears_on_payslip == True:
                if not obj[id].amount and obj[id].code in rules:
                    continue
                if obj[id].code in excludes:
                    continue
                ids.append(obj[id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        return res

    def get_payslip_deductions(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
        deductions = ['PEN', 'PAYE', 'LP', 'SAV', 'EL', 'OD']
        for id in range(len(obj)):
            if obj[id].appears_on_payslip == True:
                if not obj[id].amount:
                    continue
                if obj[id].code in deductions:
                    ids.append(obj[id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        return res

    def get_payslip_rule(self, obj, type):
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].appears_on_payslip == True:
                if obj[id].code == type:
                    ids.append(obj[id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        return res

report_sxw.report_sxw('report.ng.hr.payslip', 'hr.payslip', 'addons_aug/l10n_ng_hr_payroll/report/ng_hr_payroll.rml', parser=hr_payslip_report, header=False)
