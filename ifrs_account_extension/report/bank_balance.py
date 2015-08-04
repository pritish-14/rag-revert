# -*- coding: utf-8 -*-
##############################################################################
import time

from openerp.report import report_sxw
from account.report.common_report_header import common_report_header

class bank_balance_detail(report_sxw.rml_parse, common_report_header):
    _name = 'bank.balance.detail'

    def __init__(self, cr, uid, name, context=None):
        super(bank_balance_detail, self).__init__(cr, uid, name, context=context)
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
            'get_last_fiscalyear':self._get_last_fiscalyear, 
            'get_filter': self._get_filter,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'get_total_asset': self._get_total_asset,
        })
        self.context = context


    def _get_total_asset(self, data):
        result = {}
        ctx = self.context.copy()
        account_obj = self.pool.get('account.account')
        asset_ids = account_obj.search(self.cr, self.uid, [('type', '=', 'view'), ('user_type.name', '=', 'Asset View')])
        if asset_ids:
            result = account_obj.read(self.cr, self.uid, asset_ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        return result and result[0]['balance']

    def _get_account_balance(self, account_name):
        result = {}
        ctx = self.context.copy()
        account_obj = self.pool.get('account.account')
        account_ids = account_obj.search(self.cr, self.uid, [('name', '=', 'account_name')])
        if account_ids:
            result = account_obj.read(self.cr, self.uid, account_ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        return result and result[0]['balance']

    def _get_last_fiscalyear(self, ids):
        #self._get_fiscalyear
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).name
        return ''

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(bank_balance_detail, self).set_context(objects, data, new_ids, report_type=report_type)

    #def _add_header(self, node, header=1):
    #    if header == 0:
    #        self.rml_header = ""
    #    return True

    def _get_account(self, data):
        if data['model']=='account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(bank_balance_detail ,self)._get_account(data)

    def lines(self, form, ids=None, done=None):
        print 'PLLLL::::::::'
        def _process_child(accounts, disp_acc, parent):
                print 'accounts::::', accounts
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

        ctx = self.context.copy()

        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        inc_accs = obj_account.search(self.cr, self.uid, [('type', '=', 'view'), ('user_type.name', '=', 'Income View')])
        exp_accs = obj_account.search(self.cr, self.uid, [('type', '=', 'view'), ('user_type.name', '=', 'Expense View')])
        accs = inc_accs + exp_accs
        print 'accs::::', accs
        if accs:
            ids = accs
        parents = ids
        #child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
#        if child_ids:
#            ids = child_ids
        print 'ids 111:::::::::', ids
        ids = [account.id for account in obj_account.browse(self.cr, self.uid, ids, ctx) if account.parent_id and account.parent_id.code in ('2', '900000')]
#        print 'ids222:::', ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        print 'accounts::::::::', accounts

        self.result_acc.extend(accounts)
#        for parent in parents:
#                if parent in done:
#                    continue
#                done[parent] = 1
#                _process_child(accounts,form['display_account'],parent)
        print 'self.result_acc:::::', self.result_acc
        return self.result_acc

report_sxw.report_sxw('report.bank.balance.list', 'account.account', 'addons_aug/ifrs_account/report/bank_balance_detail.rml', parser=bank_balance_detail, header="internal")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
