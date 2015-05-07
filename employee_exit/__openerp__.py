# coding: utf-8
# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
{
    'name': ' Employee Exit ',
    'version': '1.0',
    'category': 'Human Resources',
    #'sequence': 19,
    'summary': 'This application allows management of exit of employees in the company.',
    'description': """

    """,
    "author": "Apagen Solutions Pvt. Ltd.",
    'website': 'http://www.apagen.com',
    'depends': ['hr_security','base',
        'hr'
        ],
    'data': [
        'security/ir.model.access.csv',
        'exit_view.xml',
        'exit_sequence.xml',
        'exit_workflow.xml',
        'employee_exit_data.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
