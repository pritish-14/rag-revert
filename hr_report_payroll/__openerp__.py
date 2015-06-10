# -*- coding: utf-8 -*-

{
    'name': 'Kenyan HR_Payroll',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Human Resource',
    'sequence': 2,
    'website': 'http://www.apagen.com',
    'summary': '',
    'description': """    """,
    'depends': ['hr_payroll'],
    'data': [
        'hr_payroll_view.xml',
        'kenyan_hr_payroll_data.xml',    
        'wizard/hr_report_payroll_wiz.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
