{
    'name': 'Invoicing & Payments_RAG',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'website': 'www.apagen.com',
    'summary': '',
    'description': """This application modifies invoice according to RAG""",
    'author': 'Apagen Solutions Pvt. Ltd.',
<<<<<<< HEAD
    'depends': ['account', 'account_payment','sale','partner_product_RAG', 'report_aeroo', 'medical_premium', 'brief_management'],
=======
    'depends': [
        'account',
        'account_payment',
        'sale',
        'partner_product_RAG',
        'report_aeroo',
        'medical_premium',
        'account_asset',
        'account_cancel',
        'project',
        'base_RAG',
    ],
>>>>>>> 4050613bd3a0a92a8b22c0cbd2441ad10d39072b
    'data': [
        'security/ir.model.access.csv',
        'account_invoice_view.xml',
        'view/report_invoice.xml',
        'account_invoice_workflow.xml',
        'wizard/supplier_rem_wiz_view.xml',
        'account_invoice_report.xml',
        'report/supplier_aeroo_report.xml',
        'report/partner_statement_aeroo.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
