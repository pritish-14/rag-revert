# -*- coding: utf-8 -*-

{
    'name': 'Employee Emergency Contact',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Human Resources',
    'sequence': 4,
    'website': 'http://www.apagen.com',
    'summary': '',
    'description': """This application extends the functionality of Employee Register""",
    'depends': ['hr','employee_register_RAG','base', 'hr_security'],
    'data': [
    	'security/ir.model.access.csv',
        'emp_emergency_contact_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
