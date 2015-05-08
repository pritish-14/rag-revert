{
    'name': 'Invoicing & Payments_RAG',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'website': 'www.apagen.com',
    'summary': '',
    'description': """This application modifies invoice according to RAG""",
    'author': 'Apagen Solutions Pvt. Ltd.',
    'depends': ['account', 'account_payment','sale','partner_product_RAG'],
    'data': [
        
        'account_invoice_view.xml',
        #'account_invoice_report.xml',
        #'report/supplier_aeroo_report.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
