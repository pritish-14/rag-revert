from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class product_product(osv.osv):
    _inherit = "product.template"

    _columns = {
#        'name': fields.char('Name', required=True),
        'category': fields.selection([ 
                        ('sponsorship', 'Sponsorship'),
                        ('promotion', 'Promotion'),
                        ('spot', 'Spot Adverts'),
                        ('mentions', 'Mentions'),
                        ('production', 'Production'),
                        ('classified', 'Classified'),
                        ('event', 'Event'),
                        ('banners', 'Banners'),
                        ('outdoor', 'Outdoor Activation')], 'Package'),
#        'brand_type': fields.selection([('radio','Radio'),('tv','TV')], 'Type'),   
        'package_ids': fields.one2many('product.packages.line', 'line_id', "Package Line"),
        'package_ids1': fields.one2many('product.packages.line', 'line_id1', "Package Line"),         
        'package_ids2': fields.one2many('product.packages.line', 'line_id2', "Package Line"),         
        'package_ids3': fields.one2many('product.packages.line', 'line_id3', "Package Line"),                                          
        'package_ids4': fields.one2many('product.packages.line', 'line_id4', "Package Line"),
        'package_ids5': fields.one2many('product.packages.line', 'line_id5', "Package Line"),  
        'package_ids6': fields.one2many('product.packages.line', 'line_id6', "Package Line"),  
        'package_ids7': fields.one2many('product.packages.line', 'line_id7', "Package Line"),                            
        'package_ids8': fields.one2many('product.packages.line', 'line_id8', "Package Line"),          
        'tv_package_ids': fields.one2many('product.packages.line', 'line_id9', "Package Line"),
        'tv_package_ids1': fields.one2many('product.packages.line', 'line_id10', "Package Line"),                
        'tv_package_ids2': fields.one2many('product.packages.line', 'line_id11', "Package Line"),                         
        'tv_package_ids3': fields.one2many('product.packages.line', 'line_id12', "Package Line"),                         
        'tv_package_ids4': fields.one2many('product.packages.line', 'line_id13', "Package Line"),
        'tv_package_ids5': fields.one2many('product.packages.line', 'line_id14', "Package Line"),                         
        'tv_package_ids6': fields.one2many('product.packages.line', 'line_id15', "Package Line"),                         
        'tv_package_ids7': fields.one2many('product.packages.line', 'line_id16', "Package Line"),                         
        'tv_package_ids8': fields.one2many('product.packages.line', 'line_id17', "Package Line"),                         
                                                                          
    }

    _defaults = {
        'brand_type': 'radio'
    }
        
class time_order(osv.osv):
    _name = "time.order"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    #_rec_name = 'product_id'

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('time.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()        
    
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
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
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
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

    def _invoice_exists(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for order in self.browse(cursor, user, ids, context=context):
            res[order.id] = False
            if order.invoice_ids:
                res[order.id] = True
        return res

    def _invoiced_search(self, cursor, user, obj, name, args, context=None):
        if not len(args):
            return []
        clause = ''
        sale_clause = ''
        no_invoiced = False
        for arg in args:
            if arg[1] == '=':
                if arg[2]:
                    clause += 'AND inv.state = \'paid\''
                else:
                    clause += 'AND inv.state != \'cancel\' AND sale.state != \'cancel\'  AND inv.state <> \'paid\'  AND rel.order_id = sale.id '
                    sale_clause = ',  sale_order AS sale '
                    no_invoiced = True

        cursor.execute('SELECT rel.order_id ' \
                'FROM sale_order_invoice_rel AS rel, account_invoice AS inv '+ sale_clause + \
                'WHERE rel.invoice_id = inv.id ' + clause)
        res = cursor.fetchall()
        if no_invoiced:
            cursor.execute('SELECT sale.id ' \
                    'FROM sale_order AS sale ' \
                    'WHERE sale.id NOT IN ' \
                        '(SELECT rel.order_id ' \
                        'FROM sale_order_invoice_rel AS rel) and sale.state != \'cancel\'')
            res.extend(cursor.fetchall())
        if not res:
            return [('id', '=', 0)]
        return [('id', 'in', [x[0] for x in res])]


    _columns = {
        'package': fields.many2one('package.type', 'Package'),        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('gm','Awaiting GM Approvel'),
            ('check','Awaiting Credit Check'),
            #('waiting_date', 'Waiting Schedule'),
            ('progress', 'Time Order'),
            #('manual', 'Time Order to Invoice'),
            #('invoice_except', 'Invoice Exception'),
            #('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),
        'name': fields.char('Reference', size=64, readonly=True,
                states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
        'company_id': fields.many2one('res.company', 'Company', required=False),        
        'date_order': fields.date('Order Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'advertiser_id': fields.many2one('res.partner', 'Advertiser', required=True),
        'brand_id': fields.many2one('brand', 'Brand', required=True),
        'contact_id': fields.many2one('res.partner', 'Contact', required=True),
        'product': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True),        
        'product_id': fields.selection([ 
                        ('sponsorship', 'Sponsorship'),
                        ('promotion', 'Promotion'),
                        ('Spot', 'Spot Adverts'),
                        ('mentions', 'Mentions'),
                        ('production', 'Production'),
                        ('classified', 'Classified'),
                        ('event', 'Event'),
                        ('banners', 'Banners'),
                        ('outdoor', 'Outdoor Activation')], 'Product'),
        #'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True, required='True'),       
        'user_id': fields.many2one('res.users', 'Sales Executive', required='True', select=True, track_visibility='onchange'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team', required='True', select=True, track_visibility='onchange'),   
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order."),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Currency", readonly=True),
        'invoice_ids': fields.many2many('account.invoice', 'sale_order_invoice_rel', 'order_id', 'invoice_id', 'Invoices', readonly=True, help="This is the list of invoices that have been generated for this sales order. The same sales order may have been invoiced in several times (by line for example)."),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Terms', required='True'),   
        'start_date':fields.date('Start Date', required='True'), 
        'end_date':fields.date('End Date', required='True'),   
        'sale_type': fields.selection([
            ('direct', 'Direct'),
            ('agency', 'Agency'),
            ('barter', 'Barter'),
            ], "Sales Type", required='True'),
        'note': fields.text('Terms and Conditions'),    
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'time.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'time.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'time.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'time.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'time.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'time.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
        'order_line': fields.one2many('time.order.line', 'order_id', 'Order Lines'),
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
            ], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="""This field controls how invoice and delivery operations are synchronized."""),
        'invoice_exists': fields.function(_invoice_exists, string='Invoiced', fnct_search=_invoiced_search, type='boolean', help="It indicates that sales order has at least one invoice."),
        'check': fields.boolean('Check'),        
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
    
    def create_account_invoice(self, cursor, user, ids, context=None):
        time_order = self.browse(cursor, user, ids, context) 
        for order_id in time_order:
            print "Orders", order_id.id
            if order_id.check == True:
                raise osv.except_osv('Error!', 'Invoice alredy received')                                
            inv = {
                'account_id': order_id.partner_id.id,
                'partner_id': order_id.partner_id.id,
                'brand_id': order_id.brand_id.id,
                'sales_excutive': order_id.user_id.id,
                'section_ids': order_id.section_id.id,
                'company_id': order_id.company_id and order_id.company_id.id or False,
                'date_invoice': fields.date.today(),
            }
            account_invoice_obj = self.pool.get('account.invoice')
            inv_id = account_invoice_obj.create(cursor, user, inv, context=None)
            account_invoice_line_obj = self.pool.get('account.invoice.line')
            for order_line in order_id.order_line:
                print "lines", order_line
                inv_line = {
                    'name': order_line.product_id.default_code,
                    'product_id': order_line.product_id.id,
#                    'tax_type': order_line.tax_type,
                    'subtotal': order_line.price_subtotal,
                    'quantity': order_line.product_uom_qty,
                    'price_unit': order_line.price_unit,                    
                    'type': 'out_invoice',
                    'invoice_id': inv_id,
                }
                account_invoice_line_obj.create(cursor, user, inv_line, context=None)
            account_invoice_obj.write(cursor, user, inv_id, {'check': True})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id' : inv_id,
            'type': 'ir.actions.act_window',
         }
    
    def action_abc(self, cr, uid, ids, context=None):
     	self.write(cr, uid, ids, {'state' : 'gm'})
     	list_ids = self.browse(cr, uid, ids, context)
        print ">>>>>>>>>", list_ids
        for data in list_ids:
			print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", data.date_order
			print "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", data.brand_id
			print "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC", data.user_id
			print "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", data.product_id
			print "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", data.advertiser_id
        y = self.pool.get('daily.traffic')
        data_dic ={ 
        	'create_id': data.date_order,
        	'brand_id': data.brand_id.id,
        	'responsible': data.user_id.id,
        	}
        data_id = y.create(cr, uid, data_dic)
        x = self.pool.get('daily.traffic.lines')
        new_dic = {
			'traffic_id': data_id,        		
			#'product': data.product_id.name,
        	'advertiser': data.advertiser_id.id
        }
        x.create(cr, uid, new_dic)
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
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'time.order') or '/'
        return super(time_order, self).create(cr, uid, vals, context=context)

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def action_quotation_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'time_orders', 'sale.email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'time.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'time.order', ids[0], 'quotation_sent', cr)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'time.order', ids[0], 'quotation_sent', cr)
        datas = {
                 'model': 'time.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'time.order', 'datas': datas, 'nodestroy': True}

    def test_no_product(self, cr, uid, order, context):
        for line in order.order_line:
            if line.product_id and (line.product_id.type<>'service'):
                return False
        return True

    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'time.order', ids[0], 'order_confirm', cr)

        # redisplay the record as a sales order
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'time_orders', 'view_time_order_form')
        view_id = view_ref and view_ref[1] or False,
        self.write(cr, uid, ids, {'state': 'progress'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Time Order'),
            'res_model': 'time.order',
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
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
            noprod = self.test_no_product(cr, uid, o, context)
            if (o.order_policy == 'manual') or noprod:
                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            else:
                self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
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
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'time_orders', 'view_time_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Time Order'),
            'res_model': 'time.order',
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
        time_order_line_obj = self.pool.get('time.order.line')
        for time in self.browse(cr, uid, ids, context=context):
            for inv in time.invoice_ids:
                if inv.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Cannot cancel this sales order!'),
                        _('First cancel all invoices attached to this sales order.'))
            for r in self.read(cr, uid, ids, ['invoice_ids']):
                for inv in r['invoice_ids']:
                    wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_cancel', cr)
            time_order_line_obj.write(cr, uid, [l.id for l in  time.order_line],
                    {'state': 'cancel'})
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

class time_order_line(osv.osv):

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
#            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = taxes['total']
        return res

    def _get_uom_id(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
            return result[1]
        except Exception, ex:
            return False

    def _fnct_line_invoiced(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, False)
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = this.invoice_lines and \
                all(iline.invoice_id.state != 'cancel' for iline in this.invoice_lines) 
        return res

    def _order_lines_from_invoice(self, cr, uid, ids, context=None):
        # direct access to the m2m table is the less convoluted way to achieve this (and is ok ACL-wise)
        cr.execute("""SELECT DISTINCT sol.id FROM sale_order_invoice_rel rel JOIN
                                                  sale_order_line sol ON (sol.order_id = rel.order_id)
                                    WHERE rel.invoice_id = ANY(%s)""", (list(ids),))
        return [i[0] for i in cr.fetchall()]

    _name = 'time.order.line'
    _description = 'Time Order Line'
    _columns = {
        'order_id': fields.many2one('time.order', 'Order Reference', ondelete='cascade', select=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True, related='order_id.product', store=True),
        'time_band_id': fields.many2many('time.band', 'time_order_band_rel', 'parent_id', 'child_id', 'Time Band'),
        'm': fields.integer('M'),
        'tu': fields.integer('Tu'),   
        'w': fields.integer('W'),   
        'th': fields.integer('Th'),   
        'f': fields.integer('F'),   
        'sa': fields.integer('Sa'),   
        'su': fields.integer('Su'),      
        'spots': fields.integer('Spots'),   
        'length': fields.integer('Length (Seconds)'),
        'start_date':fields.date('Start Date', required='True', related='order_id.start_date', store=True), 
        'end_date':fields.date('End Date', required='True', related='order_id.end_date', store=True), 
        'price_unit': fields.float('Price', digits_compute= dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes'),       
        'product_uom_qty': fields.integer('Quantity', digits_compute= dp.get_precision('Product UoS')),
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
        
    }

    _defaults = {
        'product_uom_qty': 1
    }

    def onchange_product(self, cr, uid, ids, product, partner_id=False, package=False, brand_id=False, lang=False, context=None):
        result = {}
        time_list = []
        context = context or {}
        if not partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the Time order.'))
        partner_obj = self.pool.get('res.partner')
        brand_obj = self.pool.get('brand')        
        product_package_obj = self.pool.get('product.packages.line')        
        product_obj = self.pool.get('product.product')
        package_id = self.pool.get('package.type').browse(cr, uid, package)
        context = {'lang': lang, 'partner_id': partner_id}
        partner = partner_obj.browse(cr, uid, partner_id)
        lang = partner.lang
        context_partner = {'lang': lang, 'partner_id': partner_id}
        product_data = product_obj.browse(cr, uid, product, context=context_partner)
        print "product type", product_data.category
        print "package", package
        print "brand_id", brand_id
        brand_type = brand_obj.browse(cr, uid, brand_id, context=context).type
        print "brand_typebrand_type", brand_type                 
        if product_data.category == 'classified' and brand_type == '1':
            for datas in product_data.package_ids1:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'classified' and brand_type == '2':
            for datas in product_data.tv_package_ids5:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'sponsorship' and brand_type == '1':
            for datas in product_data.package_ids3:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    var = data_id.id.week % 7
                    if var >= 1:
                        result['su'] = var
                        result['m'] = var
                        result['tu'] = var
                        result['th'] = var
                        result['w'] = var
                        result['f'] = var
                        result['sa'] = var
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'sponsorship' and brand_type == '2':
            for datas in product_data.tv_package_ids4:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'promotion' and brand_type == '1':
            for datas in product_data.package_ids4:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    var = data_id.id.week % 7
                    if var >= 1:
                        result['su'] = var
                        result['m'] = var
                        result['tu'] = var
                        result['th'] = var
                        result['w'] = var
                        result['f'] = var
                        result['sa'] = var
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'promotion' and brand_type == '2':
            for datas in product_data.tv_package_ids6:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'mentions' and brand_type == '1':
            for datas in product_data.package_ids2:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
                    result['length'] = data_id.id.mentions                    
        elif product_data.category == 'mentions' and brand_type == '2':
            for datas in product_data.tv_package_ids1:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    result['price_unit'] = data_id.id.price
                    result['length'] = data_id.id.mentions                                        
        if product_data.category == 'production' and brand_type == '1':
            for datas in product_data.package_ids:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'production' and brand_type == '2':
            for datas in product_data.tv_package_ids:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    result['price_unit'] = data_id.id.price
        if product_data.category == 'production' and brand_type == '1':
            for datas in product_data.package_ids:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'production' and brand_type == '2':
            for datas in product_data.tv_package_ids:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    result['price_unit'] = data_id.id.price
                    
        elif product_data.category == 'banners' and brand_type == '1':
            for datas in product_data.package_ids7:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'banners' and brand_type == '2':
            for datas in product_data.tv_package_ids3:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'event' and brand_type == '1':
            for datas in product_data.package_ids6:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'event' and brand_type == '2':
            for datas in product_data.tv_package_ids8:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'outdoor' and brand_type == '1':
            for datas in product_data.package_ids5:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'outdoor' and brand_type == '2':
            for datas in product_data.tv_package_ids7:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
                    
        elif product_data.category == 'spot' and brand_type == '1':
            for datas in product_data.package_ids:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
        elif product_data.category == 'spot' and brand_type == '2':
            for datas in product_data.tv_package_ids3:
                data_id = product_package_obj.browse(cr, uid, datas)
                if data_id.id.name.id == package_id.id:
                    for day in data_id.id.days:
                        if day.name == 'Sun':
                            result['su'] = 1
                        if day.name == 'Mon':
                            result['m'] = 1
                        if day.name == 'Tue':
                            result['tu'] = 1
                        if day.name == 'Thu':
                            result['th'] = 1
                        if day.name == 'Wed':
                            result['w'] = 1
                        if day.name == 'Fri':
                            result['f'] = 1
                        if day.name == 'Sat':
                            result['sa'] = 1
                    for day in data_id.id.timings:                            
                        time_list.append(day.id)
                    result['time_band_id'] = [(6, 0, time_list)]                
                    result['price_unit'] = data_id.id.price
                    result['spots'] = data_id.id.spots_per_day or data_id.id.spots_per_week
                    result['length'] = data_id.id.seconds                                        
        return {'value': result}    

class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def unlink(self, cr, uid, ids, context=None):
        """ Overwrite unlink method of account invoice to send a trigger to the sale workflow upon invoice deletion """
        invoice_ids = self.search(cr, uid, [('id', 'in', ids), ('state', 'in', ['draft', 'cancel'])], context=context)
        #if we can't cancel all invoices, do nothing
        if len(invoice_ids) == len(ids):
            #Cancel invoice(s) first before deleting them so that if any sale order is associated with them
            #it will trigger the workflow to put the sale order in an 'invoice exception' state
            wf_service = netsvc.LocalService("workflow")
            for id in ids:
                wf_service.trg_validate(uid, 'account.invoice', id, 'invoice_cancel', cr)
        return super(account_invoice, self).unlink(cr, uid, ids, context=context)

class time_band(osv.osv):
    _name = 'time.band'        

    _columns = {
        'name': fields.char('Name')    
        }

