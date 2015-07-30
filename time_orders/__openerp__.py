{
    'name': 'Time Orders',
    'version': '1.0',
    'category': 'Media Industry',
    'website': 'www.apagen.com',
    'summary': '',
    'description': """This application manages time orders for the media industry""",
    'author': 'Apagen Solutions Pvt. Ltd.',
    'depends': ['base_RAG', 'sale', 'brief_management'],
    'data': [
        'security/time_order_security.xml',
        'security/ir.model.access.csv',
#        'edi/time_order_action_data.xml',
        'product_data.xml',
        'time_order_view.xml',
        'time_order_sequence.xml',
        'time_order_report.xml',
        'time_order_workflow.xml',
        'time_order_action_data.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
