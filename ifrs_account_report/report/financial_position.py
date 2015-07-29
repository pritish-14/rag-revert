# -*- coding: utf-8 -*-
##############################################################################
import time
from dateutil.relativedelta import relativedelta
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header
from openerp import pooler
from datetime import datetime



class account_financial_statement(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.financial.statement'

    def __init__(self, cr, uid, name, context=None):
        
        super(account_financial_statement, self).__init__(cr, uid, name, context=context)
        self.tot_non_cur_ass = 0.0
        self.tot_cur_ass = 0.0
        self.sum_credit = 0.0
        self.tot_cur_ass_last_year = 0.0
        self.tot_non_cur_ass_last_year = 0.0
        self.tot_non_cur_lia = 0.0
        self.tot_non_cur_lia_last_year=0.0
        self.tot_cur_lia=0.0
        self.tot_cur_lia_lats=0.0
        self.tot_equ_last_year = 0.0
        self.tot_equ = 0.0
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.localcontext.update({
            'time': time,
            'get_non_current_assets': self.get_non_current_assets,
            'get_current_liability':self._get_current_liability,
            'get_non_current_liability' : self._get_non_current_liability,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear':self._get_year,
            'get_fiscal_head_year':self._get_head_year,
            'get_last_fiscalyear':self._get_last_fiscalyear, 
            'get_filter': self ._get_filter,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'get_total_asset': self._get_total_asset,
            'get_total_asset_last_year':self._get_total_asset_last_year,
            'get_lines': self._get_lines,
            'get_total_equity': self._get_total_equity,
            'get_total_equity_last_year': self._get_total_equity_last_year,
            'get_current_assets':self.get_current_assets,
            'get_total_non_curr_lia' : self._get_total_non_curr_lia,
            'get_total_non_curr_lia_last_year' : self._get_total_non_curr_lia_last_year,
            'get_total_curr_lia' : self._get_total_curr_lia,
            'get_total_curr_lia_last_year' : self._get_total_curr_lia_last_year,
            'get_total_lia' : self._get_total_lia,
            'get_total_lia_last_year': self._get_total_lia_last_year,
            'get_tot_equ_lia' : self._get_tot_equ_lia,
            'get_tot_equ_lia_last_year': self._get_tot_equ_lia_last_year
        })
        self.context = context


    def _get_total_asset(self, data):
        return self.tot_cur_ass + self.tot_non_cur_ass
        
    def _get_total_asset_last_year(self,data):
        return self.tot_cur_ass_last_year + self.tot_non_cur_ass_last_year

    def _get_total_equity(self, data):
        return self.tot_equ
    
    def _get_total_equity_last_year(self,data):
        return self.tot_equ_last_year
    
    def _get_year(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            year = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d').year
            year_str = str(year)
            return year_str[-2:]
        return ''

    def _get_head_year(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d').year
        return ''
        
    def _get_last_fiscalyear(self, data):
        fisc_year = self.pool.get('account.fiscalyear')
        account_period_obj = self.pool.get('account.period')
        date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
        if not last_year_ids:
            return False
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            year =  datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, last_year_ids[0]).date_stop,'%Y-%m-%d').year
            year_str = str(year)
            return year_str[-2:]
        return ''

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(account_financial_statement, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_account(self, data):
        if data['model']=='account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_financial_statement ,self)._get_account(data)

    def get_non_current_assets_last_year(self ,data):
        res = {}
        obj_account = self.pool.get('account.account')
        ctx = self.context.copy()
        fisc_year = self.pool.get('account.fiscalyear')
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)


        date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
        if not last_year_ids:
            return False
        ctx['fiscalyear'] = last_year_ids[0]
        accs = obj_account.search(self.cr, self.uid, ['|','|','|','|',
                                                      ('name', '=', 'Property Plant & Equipment'),
                                                       ('name', '=', 'Goodwill'),
                                                       ('name', '=', 'Other Tangible Assets'),
                                                       ('name', '=', 'Investments in Associate'),
                                                       ('name', '=', 'Other Investments'),
                                                       ('company_id','=',res_data.company_id.id)])
            
        accounts = obj_account.read(self.cr, self.uid, accs, ['name','balance'], ctx)
                
        lst_12 = {}
        for rec in accounts:
            lst_12.update({rec.get('name'):rec})
            self.tot_non_cur_ass_last_year = self.tot_non_cur_ass_last_year + rec.get('balance')
        return lst_12

    def get_non_current_assets(self,data):
        res ={}
        last_year_data = self.get_non_current_assets_last_year(data)
        obj_account = self.pool.get('account.account')
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form']['fiscalyear_id']
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        accs = obj_account.search(self.cr, self.uid, ['|','|','|','|',
                                                      ('name', '=', 'Property Plant & Equipment'),
                                                       ('name', '=', 'Goodwill'),
                                                       ('name', '=', 'Other Tangible Assets'),
                                                       ('name', '=', 'Investments in Associate'),
                                                       ('name', '=', 'Other Investments'),('company_id','=',res_data.company_id.id)])
        accounts = obj_account.read(self.cr, self.uid, accs, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        lst_13=[]
        for rec in accounts:
            lst_13.append(rec.update({'old_balance':last_year_data and last_year_data[rec['name']]['balance'] or 0.00}))
            self.tot_non_cur_ass = self.tot_non_cur_ass + rec.get('balance')
        return accounts
    
    def get_current_assets_last_year(self,data):
        res = {}
        ctx = self.context.copy()
        obj_account = self.pool.get('account.account')
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        fisc_year = self.pool.get('account.fiscalyear')
        date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
        if not last_year_ids:
            return False
        ctx['fiscalyear'] = last_year_ids[0]
        accs = obj_account.search(self.cr, self.uid, ['|','|','|','|','|',('name', '=', 'Inventories'),
                                                       ('name', '=', 'Work in Progress'),
                                                       ('name', '=', 'Trade Receivables'),
                                                       ('name', '=', 'Other Receivables'),
                                                       ('name', '=', 'Other Current Assets'),
                                                       ('name', '=', 'Cash & Bank'),
                                                       ('company_id','=',res_data.company_id.id)])
        accounts = obj_account.read(self.cr, self.uid, accs, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        lst_12 = {}
        for rec in accounts:
            lst_12.update({rec.get('name'):rec})
            self.tot_cur_ass_last_year += rec.get('balance')
        return lst_12
    
    def get_current_assets(self,data):
        res ={}
        last_year_data = self.get_current_assets_last_year(data)
        obj_account = self.pool.get('account.account')
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form']['fiscalyear_id']
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        
        accs = obj_account.search(self.cr, self.uid, ['|','|','|','|','|',('name', '=', 'Inventories'),
                                                       ('name', '=', 'Work in Progress'),
                                                       ('name', '=', 'Trade Receivables'),
                                                       ('name', '=', 'Other Receivables'),
                                                       ('name', '=', 'Other Current Assets'),
                                                       ('name', '=', 'Cash & Bank'),
                                                       ('company_id','=',res_data.company_id.id)])
        accounts = obj_account.read(self.cr, self.uid, accs, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        lst_13=[]
        for rec in accounts:
            lst_13.append(rec.update({'old_balance':last_year_data and last_year_data[rec['name']]['balance'] or 0.00}))
            self.tot_cur_ass = self.tot_cur_ass + rec.get('balance') 
        
        return accounts
    
    def _get_lines_last_year(self, form, data, ids=None, done=None):
        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}
        ctx = self.context.copy()
                
        fisc_year = self.pool.get('account.fiscalyear')
        date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
        
        if not last_year_ids:
            return False
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        
        
        ctx['fiscalyear'] = last_year_ids[0]
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        accs = obj_account.search(self.cr, self.uid, [('type', '=', 'view'), ('user_type.name', '=', 'Equity'),('company_id','=',res_data.company_id.id)])
        if accs:
            ids = [accs[0]]
    
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        ids.pop(0)
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        lst_12 = {}
        for rec in accounts:
            lst_12.update({rec.get('code'):rec})
            self.tot_equ_last_year = self.tot_equ_last_year + rec.get('balance')
        return lst_12
    
    def _get_lines(self, form,data,ids=None, done=None):
        last_year_data = self._get_lines_last_year(form, data, ids, done)
        
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
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        accs = obj_account.search(self.cr, self.uid, [('type', '=', 'view'), ('user_type.name', '=', 'Equity'),('company_id','=',res_data.company_id.id)])
        if accs:
            ids = [accs[0]]
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        ids.pop(0)

        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        new_list_new_year=[]
        lst_13=[]
        for rec in accounts:
            lst_13.append(rec.update({'old_balance':last_year_data and last_year_data[rec['code']]['balance'] or 0.00}))
            self.tot_equ = self.tot_equ + rec.get('balance')
        
        return accounts
  
    def _get_non_current_liability_last_year(self,data):
        res = {}
        ctx = self.context.copy()
        obj_account = self.pool.get('account.account')
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)

        fisc_year = self.pool.get('account.fiscalyear')
        date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
        if not last_year_ids:
            return False
        ctx['fiscalyear'] = last_year_ids[0]
        accs = obj_account.search(self.cr, self.uid, ['|','|','|',
                                                      ('name', '=', 'Long Term Borrowings'),
                                                       ('name', '=', 'Deferred Tax'),
                                                       ('name', '=', 'Long Term Provisions'),
                                                       ('name', '=', 'Project Advances (Long Term)'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        
        accounts = obj_account.read(self.cr, self.uid, accs, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        lst_12={}
        for rec in accounts:
            lst_12.update({rec.get('name'):rec})
            self.tot_non_cur_lia_last_year += rec.get('balance')
        return lst_12
        
    def _get_non_current_liability(self,data):
        res ={}
        last_year_data = self._get_non_current_liability_last_year(data)
        obj_account = self.pool.get('account.account')
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form']['fiscalyear_id']
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        accs = obj_account.search(self.cr, self.uid, ['|','|','|',
                                                      ('name', '=', 'Long Term Borrowings'),
                                                       ('name', '=', 'Deferred Tax'),
                                                       ('name', '=', 'Long Term Provisions'),
                                                       ('name', '=', 'Project Advances (Long Term)'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        
            
        accounts = obj_account.read(self.cr, self.uid, accs, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        lst_13=[]
        for rec in accounts:
            lst_13.append(rec.update({'old_balance':last_year_data and last_year_data[rec['name']]['balance'] or 0.00}))
            self.tot_non_cur_lia = self.tot_non_cur_lia + rec.get('balance')
        return accounts
  
    def _get_current_liability_last_year(self,data):
        res = {}
        ctx = self.context.copy()
        obj_account = self.pool.get('account.account')
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)

        fisc_year = self.pool.get('account.fiscalyear')
        date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
        if not last_year_ids:
            return False
        ctx['fiscalyear'] = last_year_ids[0]

        accs = obj_account.search(self.cr, self.uid, ['|','|',
                                                      ('name', '=', 'Trade Payables'),
                                                       ('name', '=', 'Other Payables'),
                                                       ('name', '=', 'Other Current Liabilities'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        
        accs += obj_account.search(self.cr, self.uid, [
                                                       ('name', '=', 'Current Portion of Longterm Borrowings'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        
        accs += obj_account.search(self.cr, self.uid, [
                                                       ('name', '=', 'Short Term Borrowings'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        accs += obj_account.search(self.cr, self.uid, [
                                                       ('name', '=', 'Short Term Provisions'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        accs += obj_account.search(self.cr, self.uid, [
                                                       ('name', '=', 'Project Advances (Short Term)'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])

        accounts = []
        for rec_id in accs:
            accounts.append(obj_account.read(self.cr, self.uid, rec_id, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx))
        lst_12 = {}
        for rec in accounts:
            lst_12.update({rec.get('name'):rec})
            self.tot_cur_lia_lats = self.tot_cur_lia_lats + rec.get('balance')
        return lst_12
    
    def _get_current_liability(self,data):
        res ={}
        last_year_data = self._get_current_liability_last_year(data)
        obj_account = self.pool.get('account.account')
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form']['fiscalyear_id']
        
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)

        accs = obj_account.search(self.cr, self.uid, ['|','|',
                                                      ('name', '=', 'Trade Payables'),
                                                       ('name', '=', 'Other Payables'),
                                                       ('name', '=', 'Other Current Liabilities'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        accs += obj_account.search(self.cr, self.uid, [
                                                       ('name', '=', 'Current Portion of Longterm Borrowings'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        accs += obj_account.search(self.cr, self.uid, [
                                                       ('name', '=', 'Short Term Borrowings'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        accs += obj_account.search(self.cr, self.uid, [
                                                       ('name', '=', 'Short Term Provisions'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        accs += obj_account.search(self.cr, self.uid, [
                                                       ('name', '=', 'Project Advances (Short Term)'),
                                                       ('company_id','=',res_data.company_id.id)
                                                      ])
        accounts = []
        for rec_id in accs:
            accounts.append(obj_account.read(self.cr, self.uid, rec_id, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx))
        lst_13=[]
        
        for rec in accounts:
            lst_13.append(rec.update({'old_balance':last_year_data and last_year_data[rec['name']]['balance'] or 0.00}))
            self.tot_cur_lia = self.tot_cur_lia + rec.get('balance')
        return accounts
#    
    def _get_total_non_curr_lia(self, data):
        return self.tot_non_cur_lia
#        
    def _get_total_non_curr_lia_last_year(self,data):
        return self.tot_non_cur_lia_last_year
#
    def _get_total_curr_lia(self, data):
        return self.tot_cur_lia 
        
    def _get_total_curr_lia_last_year(self,data):
        return self.tot_cur_lia_lats
#
    def _get_total_lia(self, data):
        return self.tot_cur_lia + self.tot_non_cur_lia
#        
    def _get_total_lia_last_year(self,data):
        return self.tot_cur_lia_lats + self.tot_non_cur_lia_last_year

    def _get_tot_equ_lia(self,data):
        return (self.tot_cur_lia + self.tot_non_cur_lia) + self._get_total_equity(data)
    def _get_tot_equ_lia_last_year(self,data):
        return (self.tot_cur_lia_lats + self.tot_non_cur_lia_last_year) + self._get_total_equity_last_year(data)
    
    
report_sxw.report_sxw('report.account.financial.statement', 'account.account', 'addons_aug/ifrs_account_report/report/financial_position.rml', parser=account_financial_statement, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
