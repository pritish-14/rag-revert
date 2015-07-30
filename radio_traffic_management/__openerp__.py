# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
{
    'name': 'Radio Traffic Management',
    'version': '1.0',
    'category': 'Media Industry',
    'summary': '',
#        'description': """
#       """,
    'author': 'Apagen Solution Pvt Ltd.',
    'website': 'http://www.apagen.com',
    'depends': ['brief_management','crm_media','time_orders'
    ],
    'data': [
    	'security/traffic_security.xml',
    	'security/ir.model.access.csv',
    	'traffic_sequence.xml',
    	'traffic_report_view.xml',
    	'traffic_workflow.xml',
    	'traffic_view.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
