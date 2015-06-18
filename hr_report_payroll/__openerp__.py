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
    'depends': ['hr_payroll', 'hr_contract'],
    'data': [
        'hr_payroll_view.xml',
        'report_payroll.xml',
        'kenyan_hr_payroll_data.xml',    
        'wizard/hr_report_payroll_wiz.xml',
        'hr_payroll_view.xml',
    	'wizard/pention_report_wiz_view.xml',
        'wizard/bank_transfer_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
