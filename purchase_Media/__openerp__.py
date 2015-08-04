# -*- coding: utf-8 -*-

{
    'name': 'Purchase_Media',
    'version': '1.0',
    'author': 'Apagen Solutions Pvt. Ltd.',
    'category': 'Media Industry',
    'sequence': 1,
    'website': 'http://www.apagen.com',
    'summary': 'This application modifies Purchase Management for Media Industry',
    'description': """This application modifies Purchase Management for Media Industry""",
    'depends': ['purchase', 'purchase_requisition','project', 'base_RAG'],
    'data': [
    	'security/ir.model.access.csv',
        'purchase_view.xml',
        'purchase_report.xml',
		#'viwes/report_purchaseorder.xml',    		
		#'views/report_purchasequotation.xml',
        #'purchase_requisition_view.xml',
        #'abc_view.xml',
        'purchase_workflow.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
