# -*- coding: utf-8 -*-

{
    'name': 'News Headlines',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Media Industry',
    'sequence': 4,
    'website': 'http://www.apagen.com',
    'summary': '',
#    'description': """    """,
    'depends': ['Winner_Tracker', 'base_RAG'],
    'data': [
        'security/news_security.xml',
        'security/ir.model.access.csv',
        'news_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
