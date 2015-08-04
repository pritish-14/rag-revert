{
    'name': 'Sale Team',
    'version': '1.0',
    'author': 'OpenERP SA',
    'category': 'Sales Management',
    'summary': 'Sales Team',
    'description': """
Using this application you can manage Sales Team  with CRM and/or Sales 
=======================================================================
 """,
    "author": "Apagen Solutions Pvt. Ltd.",
    'website': 'http://www.apagen.com',
    'depends': ['sale','sales_team','crm','time_orders','space_orders', 'base_RAG'],
    'data': [
    'security/ir.model.access.csv',
    'sales_team.xml',
    ],
    'demo': [],
    #'css': ['static/src/css/sales_team.css'],
    'installable': True,
    'auto_install': True,
    'application': True,
}
