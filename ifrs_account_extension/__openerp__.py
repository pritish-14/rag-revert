# -*- coding: utf-8 -*-

{
    'name': 'Accounting Extension',
    'version': '1.13',
    'description': """
Contains Trial Balance and General Ledger reports

    """,
    'author': 'EnerComp Solutions',
    'category': '',
    'depends': [
        'account',
        'ifrs_account',
        'account_voucher',
        'account_accountant',
        'report_aeroo',
        
        
    ],
    'demo': [],
    'data': [
        'ifrs_extension_aeroo.xml',
        'report_ifrs_account.xml',
        'ifrs_account_view.xml',
        'wizard/account_common_report_view.xml',
        'wizard/iel_account_aeroo_report_view.xml',
        'wizard/iel_account_partner_ledger_aeroo_report_view.xml',
        'wizard/account_analytic_journal_report_view.xml'
    ],
    'auto_install': False,
    'installable': True,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
