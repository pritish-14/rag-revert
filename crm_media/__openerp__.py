{
    'name': 'CRM_Media',
    'version': '1.0',
    'category': 'Media Industry',
    'website': 'www.apagen.com',
    'summary': 'This application modifies CRM module according to media industry',
  #  'description': """""",
    'author': 'Apagen Solutions Pvt. Ltd.',
    'depends': ['base','crm', 'sale', 'time_orders', 'sales_team'],
    'data': [
        'security/crm_security.xml',    
        'security/ir.model.access.csv',
    	'edi/sale_order_action_data.xml',
        'crm_lead_view.xml',
        'board_crm_view.xml',
	'menu_view.xml',        
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
