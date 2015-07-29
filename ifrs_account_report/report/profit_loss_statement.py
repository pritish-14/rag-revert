# -*- coding: utf-8 -*-
##############################################################################
import time

from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header
from openerp import pooler
from dateutil.relativedelta import relativedelta
from datetime import datetime


class profit_loss_statement(report_sxw.rml_parse, common_report_header):
    _name = 'report.profit.loss.statement'

    def __init__(self, cr, uid, name, context=None):
        super(profit_loss_statement, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.data_dict ={}
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear':self._get_year,
            'get_fiscal_head_year':self.get_fiscal_head_year,
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

    def _get_last_fiscalyear(self, data):
        #self._get_fiscalyear
        fisc_year = self.pool.get('account.fiscalyear')
        account_period_obj = self.pool.get('account.period')
        date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
        if not last_year_ids:
            return False
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            year = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, last_year_ids[0]).date_stop,'%Y-%m-%d').year
            year_str = str(year)
            return year_str[-2:]
        return ''

    def _get_year(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            year = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d').year
            year_str = str(year)
            return year_str[-2:]
        return ''    
    
    def get_fiscal_head_year(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d').year
        return ''

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(profit_loss_statement, self).set_context(objects, data, new_ids, report_type=report_type)


    def _get_account(self, data):
        if data['model']=='account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(profit_loss_statement ,self)._get_account(data)

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
                'user_type':account_rec['user_type'],
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
#                 if account_rec['child_id']:
#                     for child in account_rec['child_id']:
#                         _process_child(accounts,disp_acc,child)

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}

        ctx = self.context.copy()
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)

        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        inc_accs = obj_account.search(self.cr, self.uid, [('type', '=', 'view'), ('user_type.name', '=', 'Income View'),('company_id','=',res_data.company_id.id)])
        exp_accs = obj_account.search(self.cr, self.uid, [('type', '=', 'view'), ('user_type.name', '=', 'Expense View'),('company_id','=',res_data.company_id.id)])
        accs = inc_accs + exp_accs
        if accs:
            ids = accs
        parents = ids
        ids = [account.id for account in obj_account.browse(self.cr, self.uid, ids, ctx) if account.parent_id and account.parent_id.code in ('2')]
        accounts = obj_account.read(self.cr, self.uid, ids, ['id','type','code','name','debit','credit','balance','parent_id','level','child_id','user_type'], ctx)
        self.result_acc.extend(accounts)
        data_lst = []
        amt_lst={}
#         total_comp_income = {'code':'total_comp_income','type':'special','name':'Total Comprehensive Income for the Year','balance': 0.0,'flag':True}
#         for acc_rec in self.result_acc:
#             amt_lst.update({acc_rec.get('code'):acc_rec.get('balance',0.00)})
#             if acc_rec.get('code')=='700000':
#                 bal = float(amt_lst.get('500000')) - float(amt_lst.get('600000'))
#                 data_lst.append({'code':'profit','type':'special','name':'Gross Profit','balance': bal,'flag':True})
#             if acc_rec.get('code')=='824000':
#                 bal = (float(amt_lst.get('profit',0.00)) + float(amt_lst.get('700000'))) - (float(amt_lst.get('800000')) + float(amt_lst.get('823000'))) #+ float(amt_lst.get(7)))
#                 data_lst.append({'code':'profit_before_tax','type':'special','name':'Profit before Tax','balance': bal,'flag':True,'exp':False })
#             if acc_rec.get('code')=='900000':
#                 child_acc_ids = obj_account.search(self.cr, self.uid, [('parent_id','=',acc_rec.get('id'))], context=ctx)
#                 accounts = obj_account.read(self.cr, self.uid, child_acc_ids, ['id','type','code','name','debit','credit','balance','parent_id','level','child_id','user_type'], ctx)
#                 self.result_acc += accounts
#                 ids += child_acc_ids
#                 bal = float(amt_lst.get('profit_before_tax',0.0)) - float(amt_lst.get('824000'))
#                 data_lst.append({'code':'net_profit','type':'special','name':'Profit for the Year or Loss for the Year','balance': bal,'flag':True,'exp':False })
#             if acc_rec.get('code')=='900100' or acc_rec.get('code')=='900200' or acc_rec.get('code')=='900300' or acc_rec.get('code')=='900400':
#                 total_comp_income.update({'balance' : total_comp_income.get('balance',0.0) + acc_rec.get('balance',0.0) })
#             if acc_rec.get('code')!='900000':
#                 acc_rec.update({'flag':False})
#                 data_lst.append(acc_rec)
#         data_lst.append(total_comp_income)
        cnt = 0
        total_comp_income = {'code':'total_comp_income','type':'special','name':'Total Comprehensive Income for the Year','balance': 0.0,'flag':True}
        for acc_rec in self.result_acc:
            if acc_rec.get('code')=='900000':
                child_acc_ids = obj_account.search(self.cr, self.uid, [('parent_id','=',acc_rec.get('id'))], context=ctx)
                accounts = obj_account.read(self.cr, self.uid, child_acc_ids, ['id','type','code','name','debit','credit','balance','parent_id','level','child_id','user_type'], ctx)
                self.result_acc += accounts
                ids += child_acc_ids
            cnt = cnt + 1
            if cnt == 3:
                bal = float(amt_lst.get(1)) - float(amt_lst.get(2))
                data_lst.append({'code':'profit','type':'special','name':'Gross Profit','balance': bal,'seq':cnt,'flag':True,'exp':False})
                amt_lst.update({cnt:bal})
                cnt = cnt + 1
            if cnt == 7:
                bal = (float(amt_lst.get(3,0.00)) + float(amt_lst.get(4))) - (float(amt_lst.get(5)) + float(amt_lst.get(6)))# + float(amt_lst.get(7)))
                data_lst.append({'code':'tex_profit','type':'special','name':'Profit before Tax','balance': bal,'seq':cnt,'flag':True,'exp':False })
                amt_lst.update({cnt:bal})
                cnt = cnt + 1
            if cnt == 9:
                bal = float(amt_lst.get(7,0.00)) - float(amt_lst.get(8))
                data_lst.append({'code':'net_profit','type':'special','name':'Profit for the Year or Loss for the Year','balance': bal,'seq':cnt,'flag':True,'exp':False})
                amt_lst.update({cnt:bal})
                cnt = cnt + 1
            exp = False
            if acc_rec.get('user_type') and acc_rec.get('user_type')[1]=='Expense View':
                exp = True
            acc_rec.update({'seq':cnt,'flag':False,'exp':exp})
            
            if acc_rec.get('code')=='900100' or acc_rec.get('code')=='900200' or acc_rec.get('code')=='900300' or acc_rec.get('code')=='900400':
                total_comp_income.update({'balance' : total_comp_income.get('balance',0.0) + acc_rec.get('balance',0.0) })
            if acc_rec.get('code')!='900000':
#                 acc_rec.update({'flag':False})
                data_lst.append(acc_rec)
            amt_lst.update({cnt:acc_rec.get('balance',0.00)})
            #         if last_rec:
#             data_lst.append(last_rec)
        data_lst.append(total_comp_income)
        pre_year_data = self.last_year_lines(form, ids, done)
        main_res=[]
        for main_data in data_lst:
            old_balance = pre_year_data and pre_year_data[main_data['code']]['balance'] or 0.00
            bal = {'old_balance':str(self.formatLang(old_balance, digits=self.get_digits(dp='Account')))+' ',
                    'balance':str(self.formatLang(float(main_data.get('balance',0.00)), digits=self.get_digits(dp='Account')))+' ',}
            if old_balance < 0:
                bal.update({'old_balance':'('+str(self.formatLang(old_balance*-1, digits=self.get_digits(dp='Account')))+')'})
            if main_data.get('balance',0.00) < 0:
                bal.update({'balance':'('+str(self.formatLang(main_data.get('balance')*-1, digits=self.get_digits(dp='Account')))+')'})
        
            main_data.update(bal)
        
            main_res.append(main_data)
            if main_data['code']=='net_profit':
                main_res.append({'code':'print','type':'special','name':' ','balance':' ','old_balance':' ','seq':10, 'flag':True,'exp':False})
                main_res.append({'code':'print','type':'special','name':'Other Comprehensive Income','balance':' ','old_balance':' ','seq':10,'flag':True,'exp':False})
        return main_res#self.result_acc
    
    def last_year_lines(self, form, ids=None, done=None):

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}
        ctx = self.context.copy()
        fisc_year = self.pool.get('account.fiscalyear')
        cur_fiscal_year = pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, form['fiscalyear_id'])
        date_start = datetime.strptime(cur_fiscal_year.date_start,'%Y-%m-%d')
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date),('company_id','=',cur_fiscal_year.company_id.id )])
        if not last_year_ids:
            return False
        ctx['fiscalyear'] = last_year_ids[0]
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        profit_flag = False
        profit =0.00
        data_lst = []
        cnt=0
        amt_lst={}
#         total_comp_income = {'code':'total_comp_income','type':'special','name':'Total Comprehensive Income for the Year','balance': 0.0,'flag':True}
#         for acc_rec in self.result_acc:
#             amt_lst.update({acc_rec.get('code'):acc_rec.get('balance',0.00)})
#             if acc_rec.get('code')=='700000':
#                 bal = float(amt_lst.get('500000')) - float(amt_lst.get('600000'))
#                 data_lst.append({'code':'profit','type':'special','name':'Gross Profit','balance': bal,'flag':True})
#             if acc_rec.get('code')=='824000':
#                 bal = (float(amt_lst.get('profit',0.00)) + float(amt_lst.get('700000'))) - (float(amt_lst.get('800000')) + float(amt_lst.get('823000'))) #+ float(amt_lst.get(7)))
#                 data_lst.append({'code':'profit_before_tax','type':'special','name':'Profit before Tax','balance': bal,'seq':cnt,'flag':True,'exp':False })
#             if acc_rec.get('code')=='900000':
#                 child_acc_ids = obj_account.search(self.cr, self.uid, [('parent_id','=',acc_rec.get('id'))], context=ctx)
#                 accounts = obj_account.read(self.cr, self.uid, child_acc_ids, ['id','type','code','name','debit','credit','balance','parent_id','level','child_id','user_type'], ctx)
#                 self.result_acc += accounts
#                 ids += child_acc_ids
#                 bal = float(amt_lst.get('profit_before_tax',0.0)) - float(amt_lst.get('824000'))
#                 data_lst.append({'code':'net_profit','type':'special','name':'Profit for the Year or Loss for the Year','balance': bal,'seq':cnt,'flag':True,'exp':False })
#             if acc_rec.get('code')=='900100' or acc_rec.get('code')=='900200' or acc_rec.get('code')=='900300' or acc_rec.get('code')=='900400':
#                 total_comp_income.update({'balance' : total_comp_income.get('balance',0.0) + acc_rec.get('balance',0.0) })
#             data_lst.append(acc_rec)
#         data_lst.append(total_comp_income)
#         amt_lst={}
        cnt = 0
        total_comp_income = {'code':'total_comp_income','type':'special','name':'Total Comprehensive Income for the Year','balance': 0.0,'flag':True}
        for acc_rec  in accounts:
            cnt = cnt + 1
            if cnt == 3:
                bal = amt_lst.get(1) - amt_lst.get(2)
                data_lst.append({'code':'profit','type':'special','name':'Gross Profit','balance': bal,'seq':cnt,'flag':True})
                amt_lst.update({cnt:bal})
                cnt = cnt + 1
            if cnt == 7:
                bal = (amt_lst.get(3,0.00) + amt_lst.get(4)) - (amt_lst.get(5) + amt_lst.get(6))# + amt_lst.get(7))
                data_lst.append({'code':'tex_profit','type':'special','name':'Profit before Tax','balance': bal,'seq':cnt,'flag':True })
                amt_lst.update({cnt:bal})
                cnt = cnt + 1
            if cnt == 9:
                bal = amt_lst.get(7,0.00) - amt_lst.get(8)
                data_lst.append({'code':'net_profit','type':'special','name':'Profit for the Year or Loss for the Year','balance': bal,'seq':cnt,'flag':True})
                amt_lst.update({cnt:bal})
                cnt = cnt + 1
            if acc_rec.get('code')=='900100' or acc_rec.get('code')=='900200' or acc_rec.get('code')=='900300' or acc_rec.get('code')=='900400':
                total_comp_income.update({'balance' : total_comp_income.get('balance',0.0) + acc_rec.get('balance',0.0) })
            acc_rec.update({'seq':cnt,'flag':False})
            data_lst.append(acc_rec)
            amt_lst.update({cnt:acc_rec.get('balance',0.00)})
        data_lst.append(total_comp_income)
        dict_previous = {}
        for pre_data in data_lst:
            dict_previous.update({pre_data['code']:pre_data})
        return dict_previous#self.result_acc

report_sxw.report_sxw('report.profit.loss.statement', 'account.account', 'addons_aug/ifrs_account_report/report/statement_profit_loss.rml', parser=profit_loss_statement, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
