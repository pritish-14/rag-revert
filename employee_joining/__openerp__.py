{
    'name': ' Employee Joining ',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'This application allows management of joining/on-boarding of new employees in the company.',
    'description': """

    """,
    "author": "Apagen Solutions Pvt. Ltd.",
    'website': 'http://www.apagen.com',
    'depends': ['hr_security','base','hr_expense',
        'hr'
        ],
    'data': [
    	'security/joining_coo_security.xml',
        'security/ir.model.access.csv',
        'emp_joining_view.xml',
        'emp_joining_sequence.xml',
        'joining_workflow.xml',
        'employee_joining_data.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
