from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class space_order(osv.osv):
    _name = "space.order"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _amount_line_tax(self, cr, uid, order, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, order.tax_id, order.price_unit * (1-(order.discount or 0.0)/100.0), order.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val


    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
#            cur = order.pricelist_id.currency_id
            val1 += order.price_subtotal
#            val += self._amount_line_tax(cr, uid, order, context=context)
            res[order.id]['amount_tax'] = val
            res[order.id]['amount_untaxed'] = val1
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_default_section_id(self, cr, uid, context=None):
        """ Gives default section by checking if present in the context """
        return self._resolve_section_id_from_context(cr, uid, context=context) or False

    def _resolve_section_id_from_context(self, cr, uid, context=None):
        """ Returns ID of section based on the value of 'section_id'
            context key, or None if it cannot be resolved to a single
            Sales Team.
        """
        if context is None:
            context = {}
        if type(context.get('default_section_id')) in (int, long):
            return context.get('default_section_id')
        if isinstance(context.get('default_section_id'), basestring):
            section_name = context['default_section_id']
            section_ids = self.pool.get('crm.case.section').name_search(cr, uid, name=section_name, context=context)
            if len(section_ids) == 1:
                return int(section_ids[0][0])
        return None

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            price = order.price_unit * (1 - (order.discount or 0.0) / 100.0)
            res[order.id] = price            
        return res

    _columns = {
        'state': fields.selection([
            ('draft', 'Draft'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('gm','Awaiting GM Approvel'),
            ('check','Awaiting Credit Check'),
           # ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Space Order'),
            #('manual', 'Space Order to Invoice'),
            #('invoice_except', 'Invoice Exception'),
           # ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),
        'name': fields.char('Reference', size=64, readonly=True,
                states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
        'company_id': fields.many2one('res.company', 'Company', required=False),        
        'date_order': fields.date('Order Date', required=True),
        #, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'advertiser_id': fields.many2one('res.partner', 'Advertiser', required=True),
        'brand_id': fields.many2one('brand', 'Brand', required=True),
        'contact_id': fields.many2one('res.partner', 'Contact', required=True), 
        'sale_type': fields.selection([('direct', 'Direct'),
                                    ('agency', 'Agency'),('barter', 'Barter')], 'Sale Type', required='True'),     
        'user_id': fields.many2one('res.users', 'Sales Executive', required='True'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team', required='True'),   
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Terms', required='True'),   
        'note': fields.text('Terms and Conditions'), 
        'insertion': fields.char('Insertion', required='True'),   
        'colour_mode': fields.char('Colour Mode', required='True'),   
        'position': fields.char('Position', required='True'),   
        'publication_dates_id': fields.one2many('dates.publication', 'dates_id', 'Publication Dates', required='True'),   
        'price_unit': fields.float('Cost Per Insertion', digits_compute= dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes'),       
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            multi='sums', help="The amount without tax.", track_visibility='always', ),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            multi='sums', help="The total amount."),        
        'invoice_ids': fields.many2many('account.invoice', 'sale_order_invoice_rel', 'order_id', 'invoice_id', 'Invoices', readonly=True, help="This is the list of invoices that have been generated for this sales order. The same sales order may have been invoiced in several times (by line for example)."),
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
            ], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="""This field controls how invoice and delivery operations are synchronized."""),
    }

    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'time.order', context=c),
        'date_order': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'section_id': lambda s, cr, uid, c: s._get_default_section_id(cr, uid, c),
        'name': lambda obj, cr, uid, context: '/',
        'order_policy': 'manual',
    }
    
    def action_abc(self, cr, uid, ids, context=None):
     	self.write(cr, uid, ids, {'state' : 'gm'})
     	return True
     	
    def action_credit(self, cr, uid, ids, context=None):
    	print "000000000000000000000000000000"
     	self.write(cr, uid, ids, {'state' : 'check'})
     	print "@@@@@@@@@@@@@@@@@@@@@@@@"
     	return True
     	
    def action_reset(self, cr, uid, ids, context=None):
     	self.write(cr, uid, ids, {'state' : 'draft'})
     	return True

    def on_change_user(self, cr, uid, ids, user_id, context=None):
        """ When changing the user, also set a section_id or restrict section id
            to the ones user_id is member of. """
        if user_id:
            section_ids = self.pool.get('crm.case.section').search(cr, uid, ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)], context=context)
            if section_ids:
                return {'value': {'section_id': section_ids[0]}}
        return {'value': {}}

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'space.order') or '/'
        return super(space_order, self).create(cr, uid, vals, context=context)

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def action_quotation_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'space_orders', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'space.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'space.order', ids[0], 'quotation_sent', cr)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
            'state': 'sent',
        }

    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'space.order', ids[0], 'quotation_sent', cr)
        datas = {
                 'model': 'space.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'space.order', 'datas': datas, 'nodestroy': True}

    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'space.order', ids[0], 'order_confirm', cr)

        # redisplay the record as a sales order
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'space_orders', 'view_space_order_form')
        view_id = view_ref and view_ref[1] or False,
        self.write(cr, uid, ids, {'state': 'progress'})        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Space Order'),
            'res_model': 'space.order',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    def action_wait(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if (o.order_policy == 'manual'):
                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            else:
                self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
        return True

    def action_view_invoice(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing invoices of given sales order ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of invoices to display
        inv_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            inv_ids += [invoice.id for invoice in so.invoice_ids]
        #choose the view_mode accordingly
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result

    def copy_quotation(self, cr, uid, ids, context=None):
        id = self.copy(cr, uid, ids[0], context=None)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'space_orders', 'view_space_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Space Order'),
            'res_model': 'space.order',
            'res_id': id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        for time in self.browse(cr, uid, ids, context=context):
            for inv in time.invoice_ids:
                if inv.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Cannot cancel this sales order!'),
                        _('First cancel all invoices attached to this sales order.'))
            for r in self.read(cr, uid, ids, ['invoice_ids']):
                for inv in r['invoice_ids']:
                    wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_cancel', cr)
 #           sale_order_line_obj.write(cr, uid, [l.id for l in  time.order_line],
#                    {'state': 'cancel'})
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

class publication_dates(osv.osv):
    _name = "dates.publication"

    _columns = {
        'dates_id': fields.many2one('space.order', 'Dates'),
        'publication_dates': fields.date("Publication Dates")
        }    
