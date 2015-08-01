# -*- coding: utf-8 -*-

{
    'name': 'IFRS Accounting Reports',
    'version': '1.09',
    'description': """
IFRS Accounting Reports.
====================================

    """,
    'author': 'EnerComp Solutions',
    'category': '',
    'depends': ['account'
    ],
    'demo': [],
    'data': [
        'wizard/account_report_financial_statement.xml',
        'wizard/report_profit_loss_statement.xml',
        'wizard/account_report_value_added_statement.xml',
        'wizard/account_report_cash_flow_statement.xml',
        'wizard/account_report_changes_in_equity.xml',
        'report_ifrs_account.xml',
        'ifrs_account_report_menu.xml',
        'ifrs_account_chart.xml',
#        'wizard/report_bank_balance.xml'
    ],
    'auto_install': False,
    'installable': True,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
