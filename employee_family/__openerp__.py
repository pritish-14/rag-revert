# -*- coding: utf-8 -*-

{
    'name': ' Employee Family',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Human Resources',
    'sequence': 5,
    'website': 'http://www.apagen.com',
    'summary': '',
    'description': """This application extends the functionality of Employee Register""",
    'depends': ['hr','base','hr_security','employee_register_RAG'],
    'data': [
    	'security/ir.model.access.csv',
        'employee_family_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
