# -*- coding: utf-8 -*-
##############################################################################
import time

from openerp.report import report_sxw
from account.report.common_report_header import common_report_header

class account_financial_statement(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.financial.statement'

    def __init__(self, cr, uid, name, context=None):
        super(account_financial_statement, self).__init__(cr, uid, name, context=context)
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
        return super(account_financial_statement, self).set_context(objects, data, new_ids, report_type=report_type)

    #def _add_header(self, node, header=1):
    #    if header == 0:
    #        self.rml_header = ""
    #    return True

    def _get_account(self, data):
        if data['model']=='account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_financial_statement ,self)._get_account(data)

    def lines(self, form, ids=None, done=None):
        print 'lines:::::::', form, ids
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
        print 'ids>>>>>>>>', ids
        accs = obj_account.search(self.cr, self.uid, [('type', '=', 'view'), ('user_type.name', '=', 'Asset View')])
        print 'acccccccc::::', accs
        if accs:
            ids = [accs[0]]
        parents = ids
        print 'idssssss>>>>', ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        print 'child_ids:::::', child_ids
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        print 'accounts:::', accounts

        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)
        return self.result_acc

report_sxw.report_sxw('report.account.financial.statement', 'account.account', 'addons_aug/ifrs_account/report/financial_position.rml', parser=account_financial_statement, header="internal")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
