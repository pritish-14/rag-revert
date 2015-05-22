# -*- coding: utf-8 -*-
##############################################################################


{
    'name': 'Leave Management Extension',
    'version': '1.1',
    'author': 'EnerComp Solutions',
    'category': 'Human Resources',
    'summary': 'Leave Management Extension',
    'website': '',
    'description': """
Leave Management Extension
""",
    'depends': ['hr_holidays', 'resource', 'mail', 'employee_joining', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_holidays_security.xml',
        'holidays_data.xml',
        'hr_holiday_demo.xml',
        'hr_holiday_sequence.xml',
        'hr_holiday_extension.xml',
        'wizard/wizard_leave_check.xml',
        'hr_holiday_extension_workflow.xml'
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
