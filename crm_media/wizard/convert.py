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
        
    def _get_brand(self, cr, uid, context=None):
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

        lead = lead_obj.read(cr, uid, [active_id], ['brand_id'], context=context)[0]
        return lead['brand_id'][0] if lead['brand_id'] else False
    
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
        'advertiser_id': fields.many2one('res.partner', 'Advertiser', required=1),
        'brand_id': fields.many2one('brand', 'Brand'),
    }
    _defaults = {
        'close': False,
        'partner_id': _get_partner,
        'brand_id': _get_brand,
    }
    
         
class convert_time(osv.Model):

    _name = "convert.time"
    
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
        'start_date': fields.date('Start Date', required=1),
        'end_date': fields.date('End Date', required=1),
        'product_id': fields.selection([
            ('sponsorship', 'Sponsorship'),
            ('promotion', 'Promotion'),
            ('Spot', 'Spot Adverts'),
            ('mentions', 'Mentions'),
            ('production', 'Production'),
            ('classified', 'Classified'),
            ('event', 'Event'),
            ('banners', 'Banners'),
            ('outdoor', 'Outdoor Activation'),
            ], "Product", required='True'), 
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
    

    
    
