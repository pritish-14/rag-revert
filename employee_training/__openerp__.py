# coding: utf-8
# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
{
    'name': ' Employee Training ',
    'version': '1.0',
    'category': 'Human Resources',
    #'sequence': 19,
    'summary': 'This application enables employees to apply to attend a training.',
    'description': """

    """,
    "author": "Apagen Solutions Pvt. Ltd.",
    'website': 'http://www.apagen.com',
    'depends': ['hr_security','medical_premium',
        'hr'
        ],
    'data': [
        'security/ir.model.access.csv',
        'security/training_security.xml',
        'training_request_view.xml',
        'training_request_sequence.xml',
        'training_management_workflow.xml',
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
