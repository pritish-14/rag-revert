{
    'name': 'Space Orders',
    'version': '1.0',
    'category': 'Media Industry',
    'website': 'www.apagen.com',
    'summary': 'This application manages space orders for newspapers and print media',
    'description': """This application manages space orders for the media industry""",
    'author': 'Apagen Solutions Pvt. Ltd.',
    'depends': ['sale', 'brief_management', 'base_RAG'],
    'data': [
        'security/space_order_security.xml',
        'security/ir.model.access.csv',
        'space_order_view.xml',
        'space_order_sequence.xml',
        'space_order_report.xml',
        'space_order_workflow.xml',
        'space_menu.xml',
        'edi/space_order_action_data.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
