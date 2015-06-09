# -*- coding: utf-8 -*-

{
    'name': 'Brief Management',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Media Industry',
    'sequence': 2,
    'website': 'http://www.apagen.com',
    'summary': '',
    'description': """    """,
    'depends': ['base', 'crm', 'survey','time_orders'],
    'data': [
        'security/brief_security.xml',
        'security/ir.model.access.csv',
        'wizard/brief_form_view.xml',
        'brief_view.xml',
        'brief_sequence.xml',
        'brief_data.xml',
        'brief_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
