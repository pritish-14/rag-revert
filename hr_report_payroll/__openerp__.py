# -*- coding: utf-8 -*-

{
    'name': 'HR_Payroll_RAG',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Human Resource',
    'sequence': 2,
    'website': 'http://www.apagen.com',
    'summary': '',
    'description': """    """,
    'depends': ['hr_payroll'],
    'data': [
        'wizard/hr_report_payroll_wiz.xml',
        'hr_payroll_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
