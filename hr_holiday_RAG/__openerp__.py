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
    'depends': ['hr_holidays', 'resource', 'mail', 'medical_premium'],
    'data': [
        'security/ir.model.access.csv',
#        'security/hr_holidays_security.xml',
        'security/ir_rule.xml',
        'wizard/carry_over_view.xml',
        'holidays_data.xml',        
        'hr_holidays_view.xml',

        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
