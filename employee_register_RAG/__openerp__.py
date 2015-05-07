# -*- coding: utf-8 -*-

{
    'name': 'Employee Register_RAG',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Human Resources',
    'sequence': 1,
    'website': 'http://www.apagen.com',
    'summary': '',
    'description': """This application extends the functionality of Employee Register""",
    'depends': ['hr', 'hr_contract','base','hr_security'],
    'data': [
    	'security/ir.model.access.csv',
        'hr_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
