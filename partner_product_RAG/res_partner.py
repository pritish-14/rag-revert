from openerp.osv import fields,osv
from datetime import date

class res_partner(osv.osv):
    """ Inherits partner and adds CRM information in the partner form """
    _inherit = 'res.partner'

    _columns = {
        'dob':fields.date('Date of Birth'),    
        'pin': fields.char('PIN', size=32),
        'vat_no': fields.char('VAT No.', size=32),
        'code': fields.char('Code', size=32),
        'giro_no': fields.integer('GIRO No.'),
        'is_advertiser': fields.boolean('Advertiser'),
        'is_agency': fields.boolean('Agency'),
        'industry_id': fields.many2one('partner.industry', 'Industry')
    }

class partner_industry(osv.osv):
    _name = 'partner.industry'

    _columns = {
        'name': fields.char('Name', size=32),
    }
        
