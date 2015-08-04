# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
{
    'name': 'Winner’s Tracker',
        'version': '1.0',
        'category': 'Media Industry',
        'sequence': 14,
        'summary': '',
#        'description': """
 #       """,
        'author': 'Apagen Solution Pvt Ltd.',
        'website': 'http://www.apagen.com',
        'depends': ['mail',
            'base', 'base_RAG'
    ],
    'init_xml': [
    ],
    'data': [
        'security/winner_security.xml',
        'security/ir.model.access.csv',
        'winner_view.xml',
        'winner_workflow.xml',
        
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
