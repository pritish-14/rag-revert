from openerp.osv import osv, fields
from datetime import date

class employee_family(osv.osv):
    _name = 'employee.family'
    _columns = {
        'name': fields.char('Name', size=32),
        'identification_no': fields.char('Identification No', size=32),
        'relationship': fields.selection([('father', "Father"),
                                          ('mother', "Mother"),
                                          ('brother', "Brother"),
                                          ('sister', "Sister"),
                                          ('spouse', "Spouse")],
                                         "Relationship"),
        'anniversary': fields.date('Anniversary'),
        'phone': fields.char('Phone', size=32),
        'email': fields.char("Email", size=32),
        'occupation': fields.char('Occupation', size=32),
        'employer': fields.char('Employer', size=32),
        'emp_family_id': fields.many2one('hr.employee', 'Employee Family Id'),
    }

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'emp_family_ids':fields.one2many('employee.family', 'emp_family_id', 'Employee Family'),
    }
