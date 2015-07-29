# -*- coding: utf-8 -*-
##############################################################################
import time
import datetime as dtime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import pooler
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header

class value_added_statement(report_sxw.rml_parse, common_report_header):
    _name = 'report.value.added.statement'

    def __init__(self, cr, uid, name, context=None):
        super(value_added_statement, self).__init__(cr, uid, name, context=context)
        self.costs = 0.0
        self.pre_costs = 0.0
        self.bough = 0.0
        self.pre_bough = 0.0
        self.total_salary = 0.0
        self.pre_total_salary = 0.0
        self.total_balance = 0.0
        self.pre_total_balance = 0.0
        self.localcontext.update({
            'time': time,
            'get_fiscalyear':self._get_year,
            'get_last_fiscalyear':self._get_last_fiscalyear,
            'get_currency': self._get_currency,
            'get_company': self._get_company,
            'get_value' : self._get_value,
            'get_total' : self._get_total,
            'get_total_salary' : self._get_total_salary,
            'get_total_balance' : self._get_total_balance,
            'get_pre_total' : self._get_pre_total,
            'get_pre_total_salary' : self._get_pre_total_salary,
            'get_pre_total_balance' : self._get_pre_total_balance,
            'get_per' : self.get_per
        })
        self.context = context
    
    def get_per(self, total, value):
        total = float(total)
        value = float(value)
        if total and value:
            return (100 * value) / total
        else:
            return str(0.0)
        
    def _get_value(self,data):
        pre_data = self.pre_year_data(data)
        ctx = self.context.copy()
        fisc_year = self.pool.get('account.fiscalyear')
        date_start = dtime.datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',date_start)])
        ctx['fiscalyear'] = year_ids[0]
        
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        account_obj = self.pool.get('account.account')
        self.cr.execute("""select acc.id,acc.name
from account_account acc 
where (acc.name = 'Salaries & Wages' or acc.name = 'Other Income' 
or acc.name = 'Revenue' or acc.name = 'Value Added Tax' 
or acc.name = 'Staff Welfare' or acc.name = 'Depreciation' 
or acc.name = 'Income Tax Expenses' or acc.name = 'Finance Charges' 
or acc.name = 'Retained Earnings') and (acc.company_id = %s) """ % (res_data.company_id.id)
                               )
        account = self.cr.fetchall()
# use this code
        new_acc_ids=[]
        for (account_id,account_name) in account:
            new_acc_ids.append(account_id)
        res_data=[]
        costs=0.0
        pre_costs=0.0
        bough=0.0
        pre_bough=0.0
        total_salary=0.0
        pre_total_salary=0.0
        total_balance=0.0
        pre_total_balance=0.0
        for res in account_obj.read(self.cr, self.uid, new_acc_ids, ['name','balance'], ctx):
            res.update({'old_balance':pre_data and pre_data[res['name']]['balance'] or 0.00})
            if res.get('name') in ['Other Income','Revenue']:
                costs = costs + res.get('balance')
                pre_costs = pre_costs + res.get('old_balance')
            if res.get('name') in ['Value Added Tax']:
                bough = bough + res.get('balance') 
                pre_bough = pre_bough + res.get('old_balance') 
            if res.get('name') in ['Salaries & Wages','Staff Welfare']:
                total_salary = total_salary + res.get('balance')
                pre_total_salary = pre_total_salary + res.get('old_balance')
            if res.get('name') in ['Salaries & Wages','Staff Welfare','Depreciation','Income Tax Expenses','Finance Charges','Retained Earnings']:
                total_balance = total_balance + res.get('balance')
                pre_total_balance = pre_total_balance + res.get('old_balance')
            res_data.append(res)
        self.costs = costs
        self.pre_costs = pre_costs
        self.bough = bough - costs
        self.pre_bough = pre_bough - pre_costs
        self.total_salary = total_salary
        self.pre_total_salary = pre_total_salary
        self.total_balance = total_balance
        self.pre_total_balance = pre_total_balance
        result={}
        for rec in  res_data:
            bal={'balance':str(self.formatLang(rec.get('balance'), digits=self.get_digits(dp='Account')))+' ',
                 'old_balance':str(self.formatLang(rec.get('old_balance'), digits=self.get_digits(dp='Account')))+' '
                 }
            if rec.get('balance') < 0:
                bal.update({'balance': '('+str(self.formatLang(rec.get('balance')* -1, digits=self.get_digits(dp='Account')))+')' 
                            })
            if rec.get('old_balance') < 0:
                bal.update({'old_balance': '('+str(self.formatLang(rec.get('old_balance')* -1, digits=self.get_digits(dp='Account')))+')' 
                            })
            rec.update(bal)
            result.update({rec.get('name'):rec})
                
        return [result]
    
    def _get_total(self):
        if self.bough < 0:
            return '('+str(self.formatLang(self.bough * -1, digits=self.get_digits(dp='Account')))+')'
        return str(self.formatLang(self.bough, digits=self.get_digits(dp='Account')))
    
    def _get_pre_total(self):
        if self.pre_bough < 0:
            return '('+str(self.formatLang(self.pre_bough * -1, digits=self.get_digits(dp='Account')))+')'
        return str(self.formatLang(self.pre_bough, digits=self.get_digits(dp='Account')))+' '       
    
    def _get_total_salary(self):
        if self.total_salary < 0:
            return '('+str(self.formatLang(self.total_salary * -1, digits=self.get_digits(dp='Account')))+')'
        return str(self.formatLang(self.total_salary, digits=self.get_digits(dp='Account')))+' '       
    
    def _get_pre_total_salary(self):
        if self.pre_total_salary < 0:
            return '('+str(self.formatLang(self.pre_total_salary * -1, digits=self.get_digits(dp='Account')))+')'
        return str(self.formatLang(self.pre_total_salary, digits=self.get_digits(dp='Account')))+' '  
    
    def _get_total_balance(self):
        if self.total_balance < 0:
            return '('+str(self.formatLang(self.total_balance * -1, digits=self.get_digits(dp='Account')))+')'
        return str(self.formatLang(self.total_balance, digits=self.get_digits(dp='Account')))+ ' '  

    def _get_pre_total_balance(self):
        if self.pre_total_balance < 0:
            return '('+str(self.formatLang(self.pre_total_balance * -1, digits=self.get_digits(dp='Account')))+')'
        return str(self.formatLang(self.pre_total_balance, digits=self.get_digits(dp='Account')))+ ' '  

    
    def pre_year_data(self,data):
        ctx = self.context.copy()
        fisc_year = self.pool.get('account.fiscalyear')
        account_obj = self.pool.get('account.account')
        date_start = dtime.datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
        if not last_year_ids:
            return False
        ctx['fiscalyear'] = last_year_ids[0]
        if data['form']['filter'] == 'filter_period':
            ctx['period_from'] = data['form']['period_from']
            ctx['period_to'] = data['form']['period_to']
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form']['date_from']
            ctx['date_to'] =  data['form']['date_to']
        ctx['state'] = data['form']['target_move']
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        
        
        query = """select acc.id,acc.name
                from account_account acc 
                where (acc.name = 'Salaries & Wages' or acc.name = 'Other Income' 
                or acc.name = 'Revenue' or acc.name = 'Value Added Tax' 
                or acc.name = 'Staff Welfare' or acc.name = 'Depreciation' 
                or acc.name = 'Income Tax Expenses' or acc.name = 'Finance Charges' 
                or acc.name = 'Retained Earnings') and (acc.company_id = %s) """ % (res_data.company_id.id)
        self.cr.execute(query)
        account = self.cr.fetchall()
        old_ids=[]
        if account:
            for (ac_id,name) in account:
                old_ids.append(ac_id)
        accounts = account_obj.read(self.cr, self.uid, old_ids, ['name','balance'], ctx)
        pre_data={}
        for rec in accounts:
            pre_data.update({rec['name']:rec})
            
        return pre_data
    
    def _get_year(self, data):
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
            return datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, last_year_ids[0]).date_stop,'%Y-%m-%d').year
        return ''

report_sxw.report_sxw('report.value.added.statement', 'account.account', 'addons/ifrs_account_report/report/value_added_statement.rml', parser=value_added_statement, header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
