# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.

{
    'name': 'Preparatory Sheets',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Media Industry',
    'sequence': 5,
    'website': 'http://www.apagen.com',
    'summary': '',
#    'description': """    """,
    'depends': ['news_headlines', 'Winner_Tracker'],
    'data': [
        'security/sheet_security.xml',
        'security/ir.model.access.csv',
        'prepsheet_view.xml',
        'sheet_sequence.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
