# -*- coding: utf-8 -*-
##############################################################################
import time
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header
from openerp import pooler
from dateutil.relativedelta import relativedelta

class change_in_equity(report_sxw.rml_parse, common_report_header):
    _name = 'report.change.in.equity'

    def __init__(self, cr, uid, name, context=None):
        super(change_in_equity, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_fiscalyear':self._get_year,
            'get_last_fiscalyear':self._get_last_fiscalyear,
            'get_currency': self._get_currency,
            'get_company': self._get_company,
            'get_last_fiscalyear_start_date': self._get_last_fiscalyear_start_date,
            'get_currency': self._get_currency,
            'get_opening_bal_date_last':self._get_opening_bal_date_last,
            'get_change_equity_last':self._get_change_equity_last,
            'get_comp_income_last':self._get_comp_income_last,
            'get_bal_date_last':self._get_bal_date_last,
            'get_equity_change_current':self._get_equity_change_current,
            'get_comp_income_date_current':self._get_comp_income_date_current,
            'get_equity_bal':self._get_equity_bal,
            'get_total_equity_bal':self._get_total_equity_bal,
            'get_policy_change_entries':self._get_policy_change_entries,
            'get_equity_change_total':self._get_equity_change_total,
            'get_restated_bal':self._get_restated_bal,
            'get_dividend':self._get_dividend,
            'get_comp_income':self._get_comp_income,
            'get_total_comp_income':self._get_total_comp_income,
            'get_issue_share_current':self._get_issue_share_current,
            'get_retained_earning_credit':self._get_retained_earning_credit,
            'get_retained_earning_debit':self._get_retained_earning_debit,
        })
        self.context = context
        
    def _get_issue_share_current(self, data, acc):
        issue_share = 0.0
        acc_obj = pooler.get_pool(self.cr.dbname).get('account.account')
        move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        fisc_year = pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id'])
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        move_line_dom = [
            ('account_id','=','Issue Of Share Capital'),
            ('debit','>',0.0),
            ('date','>',fisc_year.date_start),
            ('date','<',fisc_year.date_stop),
            ('company_id','=',res_data.company_id.id)
        ]
        move_line_ids = move_line_obj.search(self.cr, self.uid, move_line_dom)
        if move_line_ids:
            move_lines = move_line_obj.browse(self.cr, self.uid, move_line_ids)
            move_ids = list(set([move_line.move_id.id for move_line in move_lines]))
            if move_ids:
                move_dom1 = [
                    ('account_id','=',acc),
                    ('credit','>',0.0),
                    ('move_id','in',move_ids),
                    ('date','>',fisc_year.date_start),
                    ('date','<',fisc_year.date_stop),
                    ('company_id','=',res_data.company_id.id)
                    ]
                move_line_ids1 = move_line_obj.search(self.cr, self.uid, move_dom1)
                if move_line_ids1:
                    for move_line in move_line_obj.browse(self.cr, self.uid, move_line_ids1):
                            issue_share += move_line.credit
        return issue_share
        
    
    def _get_comp_income(self, data, acc, diff=0):
        move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        acc_obj = pooler.get_pool(self.cr.dbname).get('account.account')
        fy_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        comp_credit = 0.0
        fy_id = data.get('form', False) and data['form'].get('fiscalyear_id', False)
        fisc_year = fy_obj.browse(self.cr, self.uid, fy_id)
        date_start = datetime.strptime(fisc_year.date_start, '%Y-%m-%d')
        last_year_date = (date_start - relativedelta(years=diff)).strftime('%Y-%m-%d %H:%M:%S')
        fisc_year_ids = fy_obj.search(self.cr, self.uid, [('date_start', '=', last_year_date)])
        if fisc_year_ids:
            fisc_year = fy_obj.browse(self.cr, self.uid, fisc_year_ids[0])
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        account_ids = acc_obj.search(self.cr, self.uid, [('name','=','Other Comprehensive Income'),('company_id','=',res_data.company_id.id)])
        if account_ids:
            child_acc_ids = acc_obj.search(self.cr, self.uid, [('id','child_of',account_ids[0]),('company_id','=',res_data.company_id.id)])
            if child_acc_ids:
                move_dom = [
                    ('account_id','in',child_acc_ids),
                    ('debit','>',0.0),
                    ('date','>',fisc_year.date_start),
                    ('date','<',fisc_year.date_stop),
                    ('company_id','=',res_data.company_id.id)
                ]
                move_line_ids = move_line_obj.search(self.cr, self.uid, move_dom)
                if move_line_ids:
                    move_lines = move_line_obj.browse(self.cr, self.uid, move_line_ids)
                    move_ids = list(set([move_line.move_id.id for move_line in move_lines]))
                    if move_ids:
                        move_dom1 = [
                            ('account_id','=',acc),
                            ('credit','>',0.0),
                            ('move_id','in',move_ids),
                            ('date','>',fisc_year.date_start),
                            ('date','<',fisc_year.date_stop),
                            ('company_id','=',res_data.company_id.id)
                        ]
                        move_line_ids1 = move_line_obj.search(self.cr, self.uid, move_dom1)
                        if move_line_ids1:
                            for move_line in move_line_obj.browse(self.cr, self.uid, move_line_ids1):
                                comp_credit += move_line.credit
        return comp_credit
    
    def _get_dividend(self, data, acc, diff=0):
        fisc_year = ""
        move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        fy_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        div_debit = 0.0
        fy_id = data.get('form', False) and data['form'].get('fiscalyear_id', False)
        fisc_year = fy_obj.browse(self.cr, self.uid, fy_id)
        date_start = datetime.strptime(fisc_year.date_start, '%Y-%m-%d')
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        if diff:
            last_year_date = (date_start - relativedelta(years=diff)).strftime('%Y-%m-%d %H:%M:%S')
            fisc_year_ids = fy_obj.search(self.cr, self.uid, [('date_start', '=', last_year_date),('company_id','=',res_data.company_id.id)])
            if fisc_year_ids:
                fisc_year = fy_obj.browse(self.cr, self.uid, fisc_year_ids[0])
        move_dom = [
            ('account_id','=','Dividends'),
            ('credit','>',0.0),
            ('date','>',fisc_year.date_start),
            ('date','<',fisc_year.date_stop),
            ('company_id','=',res_data.company_id.id)
        ]
        move_line_ids = move_line_obj.search(self.cr, self.uid, move_dom)
        if move_line_ids:
            move_lines = move_line_obj.browse(self.cr, self.uid, move_line_ids),
            move_ids = list(set([move_line[0].move_id.id for move_line in move_lines]))
            if move_ids:
                move_dom1 = [
                    ('account_id','=',acc),
                    ('debit','>',0.0),
                    ('move_id','in',move_ids),
                    ('date','>',fisc_year.date_start),
                    ('date','<',fisc_year.date_stop),
                    ('company_id','=',res_data.company_id.id)
                ]
                move_line_ids1 = move_line_obj.search(self.cr, self.uid, move_dom1)
                if move_line_ids1:
                    for move_line in move_line_obj.browse(self.cr, self.uid, move_line_ids1):
                        div_debit += move_line.debit
        
        return div_debit
        
    def _get_restated_bal(self, data, diff=0):
        accs = ['Share Capital','Revaluation Reserves','Other Components of Equity']
        total = 0.0
        for acc in accs:
            total += self._get_equity_bal(data,acc, diff=diff)
        eq_change = self._get_equity_change_total(data,'Retained Earnings', diff=diff)
        return total + eq_change
    
    def _get_equity_change_total(self, data, acc, diff=0):
        eq_bal = self._get_equity_bal(data, acc, diff=diff)
        policy_change = self._get_policy_change_entries(data, acc, diff=diff)
        return eq_bal + policy_change
    
    def _get_policy_change_entries(self, data, acc, diff=0):
        change_bal = 0.0
        move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        fy_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        acc_obj = self.pool.get('account.account')
        fisc_year = fy_obj.browse(self.cr, self.uid, data['form']['fiscalyear_id'])
        date_start = datetime.strptime(fisc_year.date_start, '%Y-%m-%d')
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        if diff:
            diff = diff - 1
            last_year_date = (date_start - relativedelta(years=diff)).strftime('%Y-%m-%d %H:%M:%S')
            fisc_year_ids = fy_obj.search(self.cr, self.uid, [('date_start', '=', last_year_date),('company_id','=',res_data.company_id.id)])
            if fisc_year_ids:
                fisc_year = fy_obj.browse(self.cr, self.uid, fisc_year_ids[0])
        account_ids = acc_obj.search(self.cr, self.uid, [('name', '=', acc),('company_id','=',res_data.company_id.id)])
        if account_ids:
            dom = [
                ('policy_change','=',True),
                ('account_id','=',acc),
                ('date','>=',fisc_year.date_start),
                ('date','<=',fisc_year.date_stop),
                ('company_id','=',res_data.company_id.id)
            ]
            move_line_ids = move_line_obj.search(self.cr, self.uid, dom)
            if move_line_ids:
                for move in move_line_obj.browse(self.cr, self.uid, move_line_ids):
                    change_bal = change_bal + move.credit - move.debit
        return change_bal
    
    def _get_total_equity_bal(self, data, diff=0):
        total = 0.0
        equity_accs = ['Share Capital', 'Retained Earnings', 'Revaluation Reserves', 'Other Components of Equity']
        for eq_ac in equity_accs:
            total += self._get_equity_bal(data, eq_ac, diff=diff)
        return total
    
    def _get_total_comp_income(self,data,diff=0):
        total = 0.0
        equity_accs = ['Retained Earnings', 'Revaluation Reserves', 'Other Components of Equity']
        for eq_ac in equity_accs:
            total += self._get_comp_income(data, eq_ac, diff=diff)
        return total
        
    def _get_equity_bal(self, data, acc, diff=0):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            acc_obj = pooler.get_pool(self.cr.dbname).get('account.account')
            date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start, '%Y-%m-%d')
            last_year_date = (date_start - relativedelta(years=diff)).strftime('%Y-%m-%d %H:%M:%S')
            fisc_year = self.pool.get('account.fiscalyear')
            last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start', '=', last_year_date)])
            ctx = self.context.copy()
            res_user_obj=self.pool.get('res.users')
            res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
            if last_year_ids: 
                ctx['fiscalyear'] = last_year_ids[0]
                account_ids = acc_obj.search(self.cr, self.uid, [('name', '=', acc),('company_id','=',res_data.company_id.id)])
                if account_ids:
                    account = acc_obj.read(self.cr, self.uid, account_ids[0], ['balance'], ctx)
                    return account['balance']
        return 0
    
    def _get_retained_earning_credit(self,data,acc,diff=0):
        move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        acc_obj = pooler.get_pool(self.cr.dbname).get('account.account')
        fy_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        retained_credit = 0.0
        fy_id = data.get('form', False) and data['form'].get('fiscalyear_id', False)
        fisc_year = fy_obj.browse(self.cr, self.uid, fy_id)
        date_start = datetime.strptime(fisc_year.date_start, '%Y-%m-%d')
        last_year_date = (date_start - relativedelta(years=diff)).strftime('%Y-%m-%d %H:%M:%S')
        fisc_year_ids = fy_obj.search(self.cr, self.uid, [('date_start', '=', last_year_date)])
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        if fisc_year_ids:
            fisc_year = fy_obj.browse(self.cr, self.uid, fisc_year_ids[0])
            
        account_ids = acc_obj.search(self.cr, self.uid, [('name','=','Revaluation Reserves'),('company_id','=',res_data.company_id.id)])
        move_dom = [
            ('account_id','=','Revaluation Reserves'),
            ('debit','>',0.0),
            ('date','>',fisc_year.date_start),
            ('date','<',fisc_year.date_stop),
            ('company_id','=',res_data.company_id.id)
        ]
        move_line_ids = move_line_obj.search(self.cr, self.uid, move_dom)
        if move_line_ids:
            move_lines = move_line_obj.browse(self.cr, self.uid, move_line_ids)
            move_ids = list(set([move_line.move_id.id for move_line in move_lines]))
            if move_ids:
                move_dom1 = [
                    ('account_id','=',acc),
                    ('credit','>',0.0),
                    ('move_id','in',move_ids),
                    ('date','>',fisc_year.date_start),
                    ('date','<',fisc_year.date_stop),
                    ('company_id','=',res_data.company_id.id)
                ]
                move_line_ids1 = move_line_obj.search(self.cr, self.uid, move_dom1)
                if move_line_ids1:
                    for move_line in move_line_obj.browse(self.cr, self.uid, move_line_ids1):
                        retained_credit += move_line.credit
        return retained_credit
 
    def _get_retained_earning_debit(self, data, acc, diff=0):
        fisc_year = ""
        move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        fy_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        retained_debit = 0.0
        fy_id = data.get('form', False) and data['form'].get('fiscalyear_id', False)
        fisc_year = fy_obj.browse(self.cr, self.uid, fy_id)
        date_start = datetime.strptime(fisc_year.date_start, '%Y-%m-%d')
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        if diff:
            last_year_date = (date_start - relativedelta(years=diff)).strftime('%Y-%m-%d %H:%M:%S')
            fisc_year_ids = fy_obj.search(self.cr, self.uid, [('date_start', '=', last_year_date)])
            if fisc_year_ids:
                fisc_year = fy_obj.browse(self.cr, self.uid, fisc_year_ids[0])
        move_dom = [
            ('account_id','=','Retained Earnings'),
            ('credit','>',0.0),
            ('date','>',fisc_year.date_start),
            ('date','<',fisc_year.date_stop),
            ('company_id','=',res_data.company_id.id)
        ]
        move_line_ids = move_line_obj.search(self.cr, self.uid, move_dom)
        if move_line_ids:
            move_lines = move_line_obj.browse(self.cr, self.uid, move_line_ids)
            move_ids = list(set([move_line.move_id and move_line.move_id.id for move_line in move_lines]))
            if move_ids:
                move_dom1 = [
                    ('account_id','=',acc),
                    ('debit','>',0.0),
                    ('move_id','in',move_ids),
                    ('date','>',fisc_year.date_start),
                    ('date','<',fisc_year.date_stop),
                    ('company_id','=',res_data.company_id.id)
                ]
                move_line_ids1 = move_line_obj.search(self.cr, self.uid, move_dom1)
                if move_line_ids1:
                    for move_line in move_line_obj.browse(self.cr, self.uid, move_line_ids1):
                        retained_debit += move_line.debit
        return retained_debit
           
    def _get_comp_income_date_current(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start, '%Y-%m-%d')
            current_year = date_start.strftime('%Y')
            return 'Total Comprehensive Income ' + current_year
        return ''
    
    def _get_equity_change_current(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start, '%Y-%m-%d')
            current_year = date_start.strftime('%Y')
            return 'Changes in Equity for ' + current_year
        return ''
    
    def _get_bal_date_last(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start, '%Y-%m-%d')
            last_year = (date_start - relativedelta(years=1)).strftime('%Y')
            return 'Balance at 31st December ' + last_year
        return ''
        
    def _get_comp_income_last(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start, '%Y-%m-%d')
            last_year = (date_start - relativedelta(years=1)).strftime('%Y')
            return 'Total Comprehensive Income ' + last_year
        return ''
    
    def _get_change_equity_last(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start, '%Y-%m-%d')
            last_year = (date_start - relativedelta(years=1)).strftime('%Y')
            return 'Changes in Equity for ' + last_year
        return ''
        
    def _get_opening_bal_date_last(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start, '%Y-%m-%d')
            last_year_date = (date_start - relativedelta(years=1)).strftime('%d/%m/%Y')
            return 'Opening Balance at ' + last_year_date
        return ''

    def _get_year(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d').year
        return ''
    
    def _get_last_fiscalyear(self, ids):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).name
        return ''

    def _get_last_fiscalyear_start_date(self, ids):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start
        return ''
    
    def _get_opening_bal_previous_year(self, data):
        return ''
        
report_sxw.report_sxw('report.change.in.equity', 'account.account', 'addons/ifrs_account_report/report/change_in_equity.rml', parser=change_in_equity, header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
