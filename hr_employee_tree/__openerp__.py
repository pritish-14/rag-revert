#Hr employee tree structure..
{
    'name':'hr_structure',
    'version': '1.1',
    'author': 'OpenERP SA',
    'category': 'Human Resources',
    'website': 'http://www.openerp.com',
    'summary': 'Heirarchycal Chart Employee',
    'description': """
Human Resources Management
==========================
    This is Application of Employee of Organization displayee in Hierarchycal View

    """,
    'depends': ['base','hr','web','base_setup','website','mail'],
    'data': [
    'employee_tree_view.xml',
    'views/document.xml',
    #'view/hr_employee_tree.xml',
    ],
    'qweb': [
        'static/src/xml/hr_employee_tree.xml'
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
