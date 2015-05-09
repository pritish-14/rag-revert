{
    'name': 'Space Orders',
    'version': '1.0',
    'category': 'Media Industry',
    'website': 'www.apagen.com',
    'summary': '',
    'description': """This application manages space orders for the media industry""",
    'author': 'Apagen Solutions Pvt. Ltd.',
    'depends': ['sale', 'brief_management', 'time_orders'],
    'data': [
        'security/space_order_security.xml',
        'security/ir.model.access.csv',
        'space_order_view.xml',
        'space_order_sequence.xml',
        'space_order_report.xml',
        'space_order_workflow.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}