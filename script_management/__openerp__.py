# -*- coding: utf-8 -*-

{
    'name': 'Script Management',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Media Industry',
    'sequence': 3,
    'website': 'http://www.apagen.com',
    'summary': '',
    'description': """    """,
    'depends': ['base', 'brief_management', 'pad_project'],
    'data': [
        'security/script_security.xml',
        'security/ir.model.access.csv',
        'script_view.xml',
        'script_sequence.xml',                
        'script_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
