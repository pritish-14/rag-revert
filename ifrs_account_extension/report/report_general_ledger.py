# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 CamptoCamp
# Copyright (c) 2006-2010 OpenERP S.A
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header
from openerp.osv import fields, osv

class account_report_general_ledger(osv.osv_memory):
    _inherit = "account.report.general.ledger"
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['landscape',  'initial_balance', 'amount_currency', 'sortby'])[0])
        if not data['form']['fiscalyear_id']:# GTK client problem onchange does not consider in save record
            data['form'].update({'initial_balance': False})
        if data['form']['landscape']:
            return { 'type': 'ir.actions.report.xml', 'report_name': 'account.general.ledger_landscape11', 'datas': data}
        return { 'type': 'ir.actions.report.xml', 'report_name': 'account.general.ledger11', 'datas': data}

class account_balance_report(osv.osv_memory):
    _inherit = "account.balance.report"
    
    _columns = {
        'account_ids': fields.many2many('account.account', 'account_balance_report_rel_ifrs', 'account_id', 'id5', 'Accounts'),
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        acc_ids = self.browse(cr, uid, ids[0], context=context).account_ids
        accounts = [acc.id for acc in acc_ids]
        data['form'].update({'account_ids' : accounts})
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance1', 'datas': data}

account_balance_report()

class account_balance1(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.account.balance1'

    def __init__(self, cr, uid, name, context=None):
        super(account_balance1, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear':self._get_fiscalyear,
            'get_filter': self._get_filter,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(account_balance1, self).set_context(objects, data, new_ids, report_type=report_type)

    #def _add_header(self, node, header=1):
    #    if header == 0:
    #        self.rml_header = ""
    #    return True
    

    def _get_account(self, data):
        if data['model']=='account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_balance1 ,self)._get_account(data)

    def lines(self, form, ids=None, done=None):
        def _process_child(accounts, disp_acc, parent):
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                    'user_type': account_rec['user_type'][1]
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                else:
                    self.result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _process_child(accounts,disp_acc,child)

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}
        print "form::::::::::::::",form
        ctx = self.context.copy()
        self.account_ids = form['account_ids']
        ctx.update({'account_ids' : self.account_ids})

        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['user_type','type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)

        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)
        return self.result_acc
    

#report_sxw.report_sxw('report.account.account.balance1', 'account.account', 'addons_aug/ifrs_account_extension/report/account_balance1.rml', parser=account_balance1, header="internal")

report_sxw.report_sxw('report.account.account.balance1', 'account.account', 'addons_aug/ifrs_account_extension/report/trial_balances.rml', parser=account_balance1, header="internal")


class account_general_ledger(report_sxw.rml_parse, common_report_header):
    _name = 'account.general.ledger.report'

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if report_type == "pdf":
            self.init_balance = data['form'].get('initial_balance')
        else:
            self.init_balance = data['datas']['form'].get('initial_balance')
        obj_move = self.pool.get('account.move.line')
        self.sortby = data['form'].get('sortby', 'sort_date')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context',{}))
        ctx2 = data['form'].get('used_context',{}).copy()
        if self.init_balance:
            ctx2.update({'initial_bal': True})
        self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        self.display_account = data['form']['display_account']
        self.target_move = data['form'].get('target_move', 'all')
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form']['fiscalyear_id']
        if data['form']['filter'] == 'filter_period':
            ctx['periods'] = data['form']['periods']
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form']['date_from']
            ctx['date_to'] =  data['form']['date_to']
        ctx['state'] = data['form']['target_move']
        self.context.update(ctx)
        if (data['model'] == 'ir.ui.menu'):
            new_ids = [data['form']['chart_account_id']]
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(account_general_ledger, self).set_context(objects, data, new_ids, report_type=report_type)

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(account_general_ledger, self).__init__(cr, uid, name, context=context)
        self.query = ""
        self.tot_currency = 0.0
        self.period_sql = ""
        self.sold_accounts = {}
        self.sortby = 'sort_date'
        self.localcontext.update( {
            'time': time,
            'lines': self.lines,
            'sum_debit_account': self._sum_debit_account,
            'sum_credit_account': self._sum_credit_account,
            'sum_balance_account': self._sum_balance_account,
            'sum_currency_amount_account': self._sum_currency_amount_account,
            'get_children_accounts': self.get_children_accounts,
            'get_fiscalyear': self._get_fiscalyear,
            'get_journal': self._get_journal,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_sortby': self._get_sortby,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
        })
        self.context = context

    def _sum_currency_amount_account(self, account):
        self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                FROM account_move_line l \
                WHERE l.account_id = %s AND %s' %(account.id, self.query))
        sum_currency = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                            FROM account_move_line l \
                            WHERE l.account_id = %s AND %s '%(account.id, self.init_query))
            sum_currency += self.cr.fetchone()[0] or 0.0
        return sum_currency

    def get_children_accounts(self, account):
        res = []
        currency_obj = self.pool.get('res.currency')
        gl_obj = self.pool.get('account.report.general.ledger')
        gl_data = gl_obj.browse(self.cr, self.uid, self.context['active_id'])
        if self.display_account == 'none':
            for acc_ids in gl_obj.browse(self.cr, self.uid, self.context['active_id']).account_ids:
                res.append(acc_ids)
            return res
        else:
            ids_acc = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            for child_account in self.pool.get('account.account').browse(self.cr, self.uid, ids_acc, context=self.context):
                sql = """
                    SELECT count(id)
                    FROM account_move_line AS l
                    WHERE %s AND l.account_id = %%s
                """ % (self.query)
                self.cr.execute(sql, (child_account.id,))
                num_entry = self.cr.fetchone()[0] or 0
                sold_account = self._sum_balance_account(child_account)
                self.sold_accounts[child_account.id] = sold_account
                if self.display_account == 'movement':
                    if child_account.type != 'view' and num_entry <> 0:
                        res.append(child_account)
                elif self.display_account == 'not_zero':
                    if child_account.type != 'view' and num_entry <> 0:
                        if not currency_obj.is_zero(self.cr, self.uid, currency, sold_account):
                            res.append(child_account)
                else:
                    res.append(child_account)
            if not res:
                return [account]
            return res

    def lines(self, account):
        """ Return all the account_move_line of account with their account code counterparts """
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted', '']
        # First compute all counterpart strings for every move_id where this account appear.
        # Currently, the counterpart info is used only in landscape mode
        sql = """
            SELECT m1.move_id,
                array_to_string(ARRAY(SELECT DISTINCT a.code
                                          FROM account_move_line m2
                                          LEFT JOIN account_account a ON (m2.account_id=a.id)
                                          WHERE m2.move_id = m1.move_id
                                          AND m2.account_id<>%%s), ', ') AS counterpart
                FROM (SELECT move_id
                        FROM account_move_line l
                        LEFT JOIN account_move am ON (am.id = l.move_id)
                        WHERE am.state IN %s and %s AND l.account_id = %%s GROUP BY move_id) m1
        """% (tuple(move_state), self.query)
        self.cr.execute(sql, (account.id, account.id))
        counterpart_res = self.cr.dictfetchall()
        counterpart_accounts = {}
        for i in counterpart_res:
            counterpart_accounts[i['move_id']] = i['counterpart']
        del counterpart_res

        # Then select all account_move_line of this account
        if self.sortby == 'sort_journal_partner':
            sql_sort='j.code, p.name, l.move_id'
        else:
            sql_sort='l.date, l.move_id'
        sql = """
            SELECT l.id AS lid, l.date AS ldate, j.code AS lcode, l.currency_id,l.amount_currency,l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, l.period_id AS lperiod_id, l.partner_id AS lpartner_id,
            m.name AS move_name, m.id AS mmove_id,per.code as period_code,
            c.symbol AS currency_code,
            i.id AS invoice_id, i.type AS invoice_type, i.number AS invoice_number,
            p.name AS partner_name,
            l.name AS name
            FROM account_move_line l
            JOIN account_move m on (l.move_id=m.id)
            LEFT JOIN res_currency c on (l.currency_id=c.id)
            LEFT JOIN res_partner p on (l.partner_id=p.id)
            LEFT JOIN account_invoice i on (m.id =i.move_id)
            LEFT JOIN account_period per on (per.id=l.period_id)
            JOIN account_journal j on (l.journal_id=j.id)
            WHERE %s AND m.state IN %s AND l.account_id = %%s ORDER by %s
        """ %(self.query, tuple(move_state), sql_sort)
        self.cr.execute(sql, (account.id,))
        res_lines = self.cr.dictfetchall()
        res_init = []
        if res_lines and self.init_balance:
            #FIXME: replace the label of lname with a string translatable
            sql = """
                SELECT 0 AS lid, '' AS ldate, '' AS lcode, COALESCE(SUM(l.amount_currency),0.0) AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, '' AS lperiod_id, '' AS lpartner_id,
                '' AS move_name, '' AS mmove_id, '' AS period_code,'' AS description,
                '' AS currency_code,
                NULL AS currency_id,
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,
                '' AS partner_name
                FROM account_move_line l
                LEFT JOIN account_move m on (l.move_id=m.id)
                LEFT JOIN res_currency c on (l.currency_id=c.id)
                LEFT JOIN res_partner p on (l.partner_id=p.id)
                LEFT JOIN account_invoice i on (m.id =i.move_id)
                JOIN account_journal j on (l.journal_id=j.id)
                WHERE %s AND m.state IN %s AND l.account_id = %%s
            """ %(self.init_query, tuple(move_state))
            self.cr.execute(sql, (account.id,))
            res_init = self.cr.dictfetchall()
        res = res_init + res_lines
        account_sum = 0.0
        for l in res:
            l['move'] = l['move_name'] != '/' and l['move_name'] or ('*'+str(l['mmove_id']))
            l['partner'] = l['partner_name'] or ''
            account_sum += l['debit'] - l['credit']
            l['progress'] = account_sum
            l['line_corresp'] = l['mmove_id'] == '' and ' ' or counterpart_accounts[l['mmove_id']].replace(', ',',')
            # Modification of amount Currency
            if l['credit'] > 0:
                if l['amount_currency'] != None:
                    l['amount_currency'] = abs(l['amount_currency']) * -1
            if l['amount_currency'] != None:
                self.tot_currency = self.tot_currency + l['amount_currency']
        return res

    def _sum_debit_account(self, account):
        if account.type == 'view':
            return account.debit
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        self.cr.execute('SELECT sum(debit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND '+ self.query +' '
                ,(account.id, tuple(move_state)))
        sum_debit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(debit) \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account.id, tuple(move_state)))
            # Add initial balance to the result
            sum_debit += self.cr.fetchone()[0] or 0.0
        return sum_debit

    def _sum_credit_account(self, account):
        if account.type == 'view':
            return account.credit
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        self.cr.execute('SELECT sum(credit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND '+ self.query +' '
                ,(account.id, tuple(move_state)))
        sum_credit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(credit) \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account.id, tuple(move_state)))
            # Add initial balance to the result
            sum_credit += self.cr.fetchone()[0] or 0.0
        return sum_credit

    def _sum_balance_account(self, account):
        if account.type == 'view':
            return account.balance
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND '+ self.query +' '
                ,(account.id, tuple(move_state)))
        sum_balance = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account.id, tuple(move_state)))
            # Add initial balance to the result
            sum_balance += self.cr.fetchone()[0] or 0.0
        return sum_balance

    def _get_account(self, data):
        if data['model'] == 'account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_general_ledger ,self)._get_account(data)

    def _get_sortby(self, data):
        if self.sortby == 'sort_date':
            return self._translate('Date')
        elif self.sortby == 'sort_journal_partner':
            return self._translate('Journal & Partner')
        return self._translate('Date')

report_sxw.report_sxw('report.account.general.ledger1', 'account.account', 'addons/ifrs_account_extension/report/general_ledger.rml', parser=account_general_ledger, header='internal')
report_sxw.report_sxw('report.account.general.ledger_landscape11', 'account.account', 'addons/ifrs_account_extension/report/general_ledger.rml', parser=account_general_ledger, header='internal landscape')
