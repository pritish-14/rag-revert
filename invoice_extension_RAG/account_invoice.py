import time
from openerp.osv import fields, osv

class ResUsers(osv.osv):
    _inherit = "res.users"
    _columns = {
        'projects': fields.many2many(
            'project.project',
            'project_user_rel',
            'uid',
            'project_id',
            'Projects')
    }

class account_invoice(osv.osv):

    _inherit = "account.invoice"
    _description = 'Invoice'

   

        
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


    _columns = {
        'date_invoice': fields.date(string='Invoice Date',
        readonly=True, states={'draft': [('readonly', False)],'awaiting_fm_approval': [('readonly', False)] }, required='True', index=True,
        help="Keep empty to use the current date", copy=False),
        'projects':fields.many2many('project.project', 'project_account_rel', 'invoice_id', 'project_id', 'Projects'),
        'invoice_line': fields.one2many('account.invoice.line', 'invoice_id', string='Invoice Lines',
         copy=True),
        'brand_id': fields.many2one('brand', 'Brand', readonly=True, states={'draft':[('readonly',False)],'awaiting_fm_approval': [('readonly', False)]}),
        'partner_statement_id': fields.many2one('partner.statement.wiz', 'Partner Statement'),   
        'supplier_code':fields.char(string='Supplier Code'),
        'regional_code':fields.char(string='Regional Code'),
        'project_code':fields.char(string='Project Code'),
        'industry_code':fields.char(string='Industry Code'),
        'product_code':fields.char(string='Product Code'),
        'section_ids': fields.many2one('crm.case.section', 'Sales Team',readonly=True, states={'draft':[('readonly',False)],'awaiting_fm_approval': [('readonly', False)]}),
        'industry_id': fields.many2one('partner.industry',"Industry", readonly=True, states={'draft':[('readonly',False)],'awaiting_fm_approval': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', string='Sales Executive', track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]}),
         'state': fields.selection([
            ('draft','Draft'),
            ('awaiting_fm_approval','Awaiting Finance Approval'),
            ('awaiting_gm_approval','Awaiting GM Approval'),
            ('awaiting_ceo_approval','Awating CEO Approval'),
            ('proforma','Proforma'),
            ('proforma2','Proforma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
        ], string='Status', index=True, readonly=True, default=None,
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice."),
             
        
             
             
             
    }
    
    

    _defaults = {
        'user_id': lambda s, cr, uid, context: uid,
        'section_ids': lambda s, cr, uid, c: s._get_default_section_id(cr, uid, c),
    }

    def on_change_user(self, cursor, user, ids, user_id, context=None):
        """ When changing the user, also set a section_id or restrict section id
            to the ones user_id is member of. """

        Users = self.pool.get('res.users')
        val = {}
        
        if user_id:
            SalesTeam = self.pool.get('crm.case.section')
            section_ids = SalesTeam.search(
                cursor, user, [
                    '|', ('user_id', '=', user_id),
                         ('member_ids', 'in', user_id)
                ], context=context
            )
            print section_ids
            val['section_ids'] = section_ids[0] if section_ids else None
            
            user = Users.browse(cursor, user, user_id, context=context)
            project_ids = [project.id for project in user.projects]
            print project_ids
            val['projects'] = project_ids
            
            return {'value': val}

        return {'value': {}}
    
    
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']
        print self
        for inv in self:
            print "------------------",inv.brand_id.name,
            brand_id = inv.brand_id.id
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv)
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env['res.users'].has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                print inv.payment_term.line_ids
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.name or inv.supplier_invoice_number or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                print enumerate(totlines)
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, brand_id, date)) for l in iml]
            line = inv.group_lines(iml, line)
            

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            move = account_move.with_context(ctx).create(move_vals)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
    
    
    
    
    def line_get_convert(self, line, part, brand_id, date):
        print "----------------------------",line.get('brand_id', False)
        print "----------------------------",line['name']        
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'][:64],
            'brand_id':brand_id,
            'date': date,
            'debit': line['price']>0 and line['price'],
            'credit': line['price']<0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_lines': line.get('analytic_lines', []),
            'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'tax_code_id': line.get('tax_code_id', False),
            'tax_amount': line.get('tax_amount', False),
            'ref': line.get('ref', False),
            'quantity': line.get('quantity',1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uos_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
        }


class account_invoice(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
        'brand_id': fields.many2one('brand', 'Brand', related='invoice_id.brand_id', store=True, readonly=True),
        'industry_id': fields.many2one('partner.industry',"Industry", related='invoice_id.industry_id', store=True, readonly=True),
        
        'brand_ids': fields.related('invoice_id', 'brand_id', type="many2one", relation="brand", string="Brand"),
        'industry_ids': fields.related('invoice_id','industry_id', type="many2one", relation='partner.industry', string="Industry"),
    }
    
    
class account_invoice1(osv.osv):

    def _get_invoice(self, cursor, user, context=None):
        
        if context is None: context = {}
        invoice_id = context.get('invoice_id', False)
        return invoice_id


    _inherit = "account.voucher"
    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'payment_ids':fields.many2many('account.move.line', string='Payments'),
        }
        

    _defaults = {
        'invoice_id': _get_invoice,
    }

    def print_supplier_report(self, cursor, user, ids, context=None):
    
        value = self.browse(cursor, user, ids, context=context) 
        
        """
        print ">>>-date :",str(value.date)
        print  ">>>-Id :",str(value.partner_id.id)
        print  ">>>- amount",str(value.amount)
        print  ">>>-number :",str(value.number)
        print  ">>>-reference :",str(value.reference)
        for line in value.line_dr_ids:
            print "name :",str(line.move_line_id.name)
            print "original amt :",str(line.amount_original)
            print "due amt :",str(line.amount_unreconciled)
            print line.move_line_id.invoice.number
            print line.move_line_id.invoice.supplier_invoice_number
        print context
        """
        
        if context is None:
            context= {}
    
        datas = {
             'ids': ids,
             'model': 'account.voucher',
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'supplier_aeroo_report_xls',
            'datas': datas,
        }
        
       
       
'''class product_template(osv.Model):
    _inherit = 'product.template'
    
    def _get_buy_route(self, cr, uid, context=None):
        
        buy_route = self.pool.get('ir.model.data').xmlid_to_res_id(cr, uid, 'purchase.route_warehouse0_buy')
        if buy_route:
            return [buy_route]
        return []

    def _purchase_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        for template in self.browse(cr, uid, ids, context=context):
            res[template.id] = sum([p.purchase_count for p in template.product_variant_ids])
        return res

    _columns = {
        'purchase_ok': fields.boolean('Can be Purchased', help="Specify if the product can be selected in a purchase order line."),
        'purchase_count': fields.function(_purchase_count, string='# Purchases', type='integer'),
    }

    _defaults = {
        'purchase_ok': 0,
        'route_ids': _get_buy_route,
    }

    def action_view_purchases(self, cr, uid, ids, context=None):
        products = self._get_products(cr, uid, ids, context=context)
        result = self._get_act_window_dict(cr, uid, 'purchase.action_purchase_line_product_tree', context=context)
        result['domain'] = "[('product_id','in',[" + ','.join(map(str, products)) + "])]"
        return result

class product_product(osv.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    
    def _purchase_count(self, cr, uid, ids, field_name, arg, context=None):
        Purchase = self.pool['purchase.order']
        return {
            product_id: Purchase.search_count(cr,uid, [('order_line.product_id', '=', product_id)], context=context) 
            for product_id in ids
        }

    _columns = {
        'purchase_count': fields.function(_purchase_count, string='# Purchases', type='integer'),
    }'''

