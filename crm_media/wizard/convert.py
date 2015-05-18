# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

class convert_space(osv.Model):

    _name = "convert.space"
    
    def _get_partner(self, cr, uid, context=None):
        """
        This function gets default value for partner_id field.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param context: A standard dictionary for contextual values
        @return: default value of partner_id field.
        """
        if context is None:
            context = {}

        lead_obj = self.pool.get('crm.lead')
        active_id = context and context.get('active_id', False) or False
        if not active_id:
            return False

        lead = lead_obj.read(cr, uid, [active_id], ['partner_id'], context=context)[0]
        return lead['partner_id'][0] if lead['partner_id'] else False
    
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain=[('customer','=',True)]),
        'close': fields.boolean('Mark Won', help='Check this to close the opportunity after having created the sales order.'),
        'insertion': fields.char('Insertion', required=1),
        'colour_mode': fields.char('Colour Mode', required=1),
        'position': fields.char('Position', required=1),
        'payment_id': fields.many2one('account.payment.term', 'Payment Terms', required=1),
        'sale_type': fields.selection([
            ('direct', 'Direct'),
            ('agency', 'Agency'),
            ('barter', 'Barter'),
            ], "Sales Type", required='True'),
        'contact_id': fields.many2one('res.partner', 'Contact', required=1),
        'advertiser_id': fields.many2one('res.partner', 'Advertiser', required=1)
    }
    _defaults = {
        'close': False,
        'partner_id': _get_partner,
    }
    
    def action_space(self, cr, uid, ids, context=None):
     	#self.write(cr, uid, ids, {'state' : 'gm'})
     	list_ids = self.pool.get('crm.lead').browse(cr, uid, ids, context=context)
        print ">>>>>>>>>", list_ids
        for data in list_ids:
			print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", data.partner_id
			print "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", data.brand_id
			print "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC", data.user_id
			print "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", data.section_id
        x = self.pool.get('convert.space').browse(cr, uid, ids, context=context)
        y = self.pool.get('space.order')
        data_dic ={ 
        	'partner_id': data.partner_id.id,
        	'brand_id': data.brand_id.id,
        	'user_id': data.user_id.id,
        	'section_id': data.section_id.id,
        	'advertiser_id': x.advertiser_id.id,
        	'insertion': x.insertion,        		
			'colour_mode': x.colour_mode,
        	'position': x.position,
        	'payment_term_id': x.payment_id.id,
        	'sale_type': x.sale_type,
        	'contact_id': x.contact_id.id,
        	}
        data_id = y.create(cr, uid, data_dic)
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'space.order',
            'res_id' : data_id,
            'type': 'ir.actions.act_window',
         }

    
    
