# -*- coding: utf-8 -*-

{
    'name': 'Employee Next of Kin',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Human Resources',
    'sequence': 3,
    'website': 'http://www.apagen.com',
    'summary': '',
    'description': """This application extends the functionality of Employee Register""",
    'depends': ['hr','employee_register_RAG','base'],
    'data': [
    	 'security/ir.model.access.csv',
        'employee_nok_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
