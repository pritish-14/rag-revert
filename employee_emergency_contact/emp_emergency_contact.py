from openerp.osv import osv, fields
from datetime import date

class emp_emergency_contact(osv.osv):
    _name = 'emp.emergency.contact'
    _columns = {
        'surname': fields.char('Surname', size=32),
        'name': fields.char('First & Middle Name', size=32),
        'relationship': fields.char("Relationship", size=32),
        'place_of_work': fields.char('Place of Work', size=32),
        'mobile': fields.char('Mobile', size=32),
        'office_telephone': fields.char("Office Telephone", size=32),
        'emp_emergency_contact_id': fields.many2one('hr.employee', 'Emergency Contact Id'),
    }

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'emp_emergency_contact_ids':fields.one2many('emp.emergency.contact', 'emp_emergency_contact_id', 'Employee Emergency Contact'),
    }
