{
    'name': 'Asset_Straight Line Method',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'website': 'www.apagen.com',
    'summary': '',
    'description': """This application modifies Asset Management module according to RAG""",
    'author': 'Apagen Solutions Pvt. Ltd.',
    'depends': ['account', 'account_asset', 'invoice_extension_RAG','stock'],
    'data': [
        'security/ir.model.access.csv',
        'account_asset_view.xml',
        'wizard/asset_register_wiz_view.xml',
        'report/asset_aeroo_report.xml',            
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
