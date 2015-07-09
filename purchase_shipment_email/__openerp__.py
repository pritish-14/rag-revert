# -*- coding: utf-8 -*-

{
    'name': 'Shipment Email',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Media Industry',
    'sequence': 1,
    'website': 'http://www.apagen.com',
    'summary': 'This application will mail the reminder for the shipments '\
               'that are pending to be delivered.',
    'description': """
      This application will mail the reminder for the shipments 
      that are pending to be delivered.
    """,
    'depends': ['purchase'],
    'data': [
        'wizard/send_email_view.xml',
        'shipment_view_email.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
