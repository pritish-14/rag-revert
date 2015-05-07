from openerp.osv import osv, fields
from datetime import date

class next_of_kin(osv.osv):
    _name = 'employee.nok'
    _columns = {
        'surname1': fields.char('Surname', size=32),
        'name': fields.char('First & Middle Name', size=32),
        'relationship': fields.char("Relationship", size=32),
        'place_of_work': fields.char('Place of Work', size=32),
        'mobile': fields.char('Mobile', size=32),
        'email': fields.char('Email'),
        'office_telephone': fields.char("Office Telephone", size=32),
        'emp_nok_id': fields.many2one('hr.employee', 'NOK Id'),
    }

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'emp_nok_ids':fields.one2many('employee.nok', 'emp_nok_id', 'Employee NOK'),
    }
