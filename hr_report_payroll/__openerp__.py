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
        'kenyan_hr_payroll_data.xml',    
        'wizard/hr_report_payroll_wiz.xml',
        'hr_payroll_view.xml',
<<<<<<< HEAD
	'wizard/pention_report_wiz_view.xml',
=======
        'wizard/bank_transfer_view.xml',
>>>>>>> ba82df1d09afd9cc6da0a6fcdc8bf06088e948a9
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
