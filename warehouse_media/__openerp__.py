# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
{
    'name': 'Warehouse_RAG',
        'version': '1.0',
        'category': 'Warehouse',
        'sequence': 14,
        'summary': 'This application modifies warehouse management for media industry',
#        'description': """
 #       """,
        'author': 'Apagen Solution Pvt Ltd.',
        'website': 'http://www.apagen.com',
        'depends': ['stock','purchase'
    ],
    'init_xml': [
    ],
    'data': [
    	'security/ir.model.access.csv',
    	'views/report_stockpicking.xml',
    	'views/report_stockinventory.xml',
        'warehouse_media_view.xml',
    	'stock_report.xml',
        
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
