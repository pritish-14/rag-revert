from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import time
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions

from openerp import netsvc
from openerp import pooler

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _columns = {
        'description': fields.char('Description', size=64),
    }
    
    def _query_get(self, cr, uid, obj='l', context=None):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalperiod_obj = self.pool.get('account.period')
        account_obj = self.pool.get('account.account')
        fiscalyear_ids = []
        if context is None:
            context = {}
        initial_bal = context.get('initial_bal', False)
        company_clause = " "
        if context.get('company_id', False):
            company_clause = " AND " +obj+".company_id = %s" % context.get('company_id', False)
        if not context.get('fiscalyear', False):
            if context.get('all_fiscalyear', False):
                #this option is needed by the aged balance report because otherwise, if we search only the draft ones, an open invoice of a closed fiscalyear won't be displayed
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [])
            else:
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('state', '=', 'draft')])
        else:
            #for initial balance as well as for normal query, we check only the selected FY because the best practice is to generate the FY opening entries
            fiscalyear_ids = [context['fiscalyear']]

        fiscalyear_clause = (','.join([str(x) for x in fiscalyear_ids])) or '0'
        state = context.get('state', False)
        where_move_state = ''
        where_move_lines_by_date = ''

        if context.get('date_from', False) and context.get('date_to', False):
            if initial_bal:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date < '" +context['date_from']+"')"
            else:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date >= '" +context['date_from']+"' AND date <= '"+context['date_to']+"')"

        if state:
            if state.lower() not in ['all']:
                where_move_state= " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE account_move.state = '"+state+"')"
        if context.get('period_from', False) and context.get('period_to', False) and not context.get('periods', False):
            if initial_bal:
                period_company_id = fiscalperiod_obj.browse(cr, uid, context['period_from'], context=context).company_id.id
                first_period = fiscalperiod_obj.search(cr, uid, [('company_id', '=', period_company_id)], order='date_start', limit=1)[0]
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, first_period, context['period_from'])
            else:
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, context['period_from'], context['period_to'])
        if context.get('periods', False):
            if initial_bal:
                query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s)) %s %s" % (fiscalyear_clause, where_move_state, where_move_lines_by_date)
                period_ids = fiscalperiod_obj.search(cr, uid, [('id', 'in', context['periods'])], order='date_start', limit=1)
                if period_ids and period_ids[0]:
                    first_period = fiscalperiod_obj.browse(cr, uid, period_ids[0], context=context)
                    ids = ','.join([str(x) for x in context['periods']])
                    query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) AND date_start <= '%s' AND id NOT IN (%s)) %s %s" % (fiscalyear_clause, first_period.date_start, ids, where_move_state, where_move_lines_by_date)
            else:
                ids = ','.join([str(x) for x in context['periods']])
                query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) AND id IN (%s)) %s %s" % (fiscalyear_clause, ids, where_move_state, where_move_lines_by_date)
        else:
            query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s)) %s %s" % (fiscalyear_clause, where_move_state, where_move_lines_by_date)

        if initial_bal and not context.get('periods', False) and not where_move_lines_by_date:
            #we didn't pass any filter in the context, and the initial balance can't be computed using only the fiscalyear otherwise entries will be summed twice
            #so we have to invalidate this query
            raise osv.except_osv(_('Warning!'),_("You have not supplied enough arguments to compute the initial balance, please select a period and a journal in the context."))
        print "context::::::account_ids::::::",context.get('account_ids')
        if context.get('journal_ids', False):
            query += ' AND '+obj+'.journal_id IN (%s)' % ','.join(map(str, context['journal_ids']))
        if context.get('account_ids', False):
            query += ' AND '+obj+'.account_id IN (%s)' % ','.join(map(str, context.get('account_ids')))
        if context.get('chart_account_id'):
            child_ids = account_obj._get_children_and_consol(cr, uid, [context['chart_account_id']], context=context)
            query += ' AND '+obj+'.account_id IN (%s)' % ','.join(map(str, child_ids))
        
        query += company_clause
        return query
    
    def _update_check(self, cr, uid, ids, context=None):
        done = {}
        for line in self.browse(cr, uid, ids, context=context):
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
            if line.move_id.state not in ('draft', 'waiting_for_approval') and (not line.journal_id.entry_posted):
                raise osv.except_osv(_('Error!'), _('You cannot do this modification on a confirmed entry. You can just change some non legal fields or you must unconfirm the journal entry first.\n%s.') % err_msg)
            if line.reconcile_id:
                raise osv.except_osv(_('Error!'), _('You cannot do this modification on a reconciled entry. You can just change some non legal fields or you must unreconcile first.\n%s.') % err_msg)
            t = (line.journal_id.id, line.period_id.id)
            if t not in done:
                self._update_journal_check(cr, uid, line.journal_id.id, line.period_id.id, context)
                done[t] = True
        return True
    
class account_move(osv.osv):
    _inherit = "account.move"
    
    def _group_readonly(self, cr, uid, ids, name, args, context=None):
        res = {}

        model_obj = self.pool.get('ir.model.data')

        users = []
        justread = False

        data = self.browse(cr, uid, ids[0], context=context)

        if data.state == 'waiting_for_approval':
            manager_group = model_obj.get_object(cr, uid, 'account', 'group_account_manager')
            manager_users = [user.id for user in manager_group.users]
            if manager_users:
                users.extend(manager_users)

            coo_group = model_obj.get_object(cr, uid, 'invoice_extension', 'group_account_coo')
            coo_users = [user.id for user in coo_group.users]
            if coo_users:
                users.extend(coo_users)

            md_group = model_obj.get_object(cr, uid, 'invoice_extension', 'group_account_md')
            md_users = [user.id for user in md_group.users]
            if md_users:
                users.extend(md_users)
# 
        if uid not in users and data.state != 'draft':
            justread = True
        
        res[ids[0]] = justread
        return res
    
    _columns = {
        'state': fields.selection([('draft','Unposted'), ('waiting_for_approval', 'Waiting For Approval'), ('posted','Posted')], 'Status', required=True, readonly=True,
            help='All manually created new journal entries are usually in the status \'Unposted\', but you can set the option to skip that status on the related journal. In that case, they will behave as journal entries automatically created by the system on document validation (invoices, bank statements...) and will be created in \'Posted\' status.'),
        'group_readonly': fields.function(_group_readonly, string='Group Readonly', type='boolean'),
        'journal': fields.many2one('product.product', 'Journal', required=True),
    }
    
    def button_waiting_for_approval(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state' : 'waiting_for_approval'}, context=context)
        return True
    
    def button_reset(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        return True
    
    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)
 
        if not valid_moves:
            raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
        obj_sequence = self.pool.get('ir.sequence')
        for move in self.browse(cr, uid, valid_moves, context=context):
            if move.name =='/':
                new_name = False
                journal = move.journal_id
 
                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                        new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                    else:
                        raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))
 
                if new_name:
                    self.write(cr, uid, [move.id], {'name':new_name})
            state = move.state
        if state != 'waiting_for_approval':
            cr.execute('UPDATE account_move '\
                       'SET state=%s '\
                       'WHERE id IN %s',
                       ('waiting_for_approval', tuple(valid_moves),))
        else:
            cr.execute('UPDATE account_move '\
                       'SET state=%s '\
                       'WHERE id IN %s',
                       ('posted', tuple(valid_moves),))
        return True
    
#     def button_validate(self, cr, uid, ids, context=None):
#         for move in self.browse(cr, uid, ids, context=context):
#             print':::::::::move',move.ref
#             for line in move.line_id:
#                 if not line.description:
#                     raise osv.except_osv(_('Warning!'),
#                                          _('Please fill Description in journal Items before validating Journal Entry.'))
#         return super(account_move, self).button_validate(cr, uid, ids, context=context)

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'comment': fields.text('Additional Information', required=True, readonly=True, states={'draft':[('readonly',False)]}),
    }

#     def action_move_create(self, cr, uid, ids, context=None):
#         move_line_obj = self.pool.get('account.move.line')
#         result = super(account_invoice, self).action_move_create(cr, uid, ids, context=context)
#         for inv in self.browse(cr, uid, ids, context=context):
#             if inv.move_id:
#                 for line in inv.move_id.line_id:
#                     move_line_obj.write(cr, uid, [line.id], {'description': inv.comment or ''})
#         return True

    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines"""
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
            company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
            # check if taxes are all computed
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            # I disabled the check_total feature
            group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
            group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
            if group_check_total and uid in [x.id for x in group_check_total.users]:
                if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
                    raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += ait_obj.move_line_get(cr, uid, inv.id)

            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
            acc_id = inv.account_id.id

            name = inv['name'] or inv['supplier_invoice_number'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = payment_term_obj.compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                ctx.update({'date': inv.date_invoice})
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p \
                                and amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })

            date = inv.date_invoice or time.strftime('%Y-%m-%d')

            part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

            line = self.group_lines(cr, uid, iml, line, inv)

            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise osv.except_osv(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)

            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
#                 'state' : 'waiting_for_approval'
            }
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update(company_id=inv.company_id.id,
                       account_period_prefer_normal=True)
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id

            ctx.update(invoice=inv)
            move_id = move_obj.create(cr, uid, move, context=ctx)
            move_obj.post(cr, uid, [move_id], context=ctx)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
        self._log_event(cr, uid, ids)
        return True

class account_voucher(osv.osv):
    _inherit = "account.voucher"
    _columns = {
        'narration':fields.text('Notes', readonly=True, required=True, states={'draft':[('readonly',False)]}),
    }
    
    
    def action_move_line_create(self, cr, uid, ids, context=None):
        
        move_line_obj = self.pool.get('account.move.line')
        result = super(account_voucher, self).action_move_line_create(cr, uid, ids, context=context)
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                for line in voucher.move_id.line_id:
                    move_line_obj.write(cr, uid, [line.id], {'description': voucher.narration or ''})
        return True        



