# -*- coding: utf-8 -*-

{
    'name': 'Employee Contract RAG',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Human Resources',
    'sequence': 6,
    'website': 'http://www.apagen.com',
    'summary': '',
    'description': """This application extends the functionality of Employee Contract""",
    'depends': ['hr_contract', 'hr_contract_init', 'hr_contract_reference', 'hr_payroll_account', 'employee_register_RAG'],
    'data': [
        'security/ir.model.access.csv',        
        'hr_contract_view.xml',
        'hr_contract_template.xml',
        'hr_contract_scheduler.xml',
        'wizard/probation_period_wiz_view.xml',

        'report/probation_aeroo_report.xml', 
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
