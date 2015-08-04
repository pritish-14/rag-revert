# -*- coding: utf-8 -*-
##############################################################################
import time
from dateutil.relativedelta import relativedelta
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header
from datetime import datetime
from openerp import pooler


class cash_flow_statement(report_sxw.rml_parse, common_report_header):
    _name = 'report.cash.flow.statement'
  
    def __init__(self, cr, uid, name, context=None):

        super(cash_flow_statement, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_fiscalyear':self._get_year,
            'get_last_fiscalyear':self._get_last_fiscalyear,
            'get_currency': self._get_currency,
            'get_company': self._get_company,
            'get_year' : self._get_year,
            'get_profit_loss_before_tax' :self._get_profit_loss_before_tax,
            'get_profit_loss_before_tax_last_year':self._get_profit_loss_before_tax_last_year,
            'get_depreciation' : self._get_depreciation,
            'get_depreciation_last_year': self._get_depreciation_last_year,
            'get_investment':self._get_investment,
            'get_investment_last_year':self._get_investment_last_year,
            'get_amortization':self._get_amortization,
            'get_amortization_last_year':self._get_amortization_last_year,
            'get_sale_of_fixed_assets':self._get_sale_of_fixed_assets,
            'get_sale_of_fixed_assets_last_year':self._get_sale_of_fixed_assets_last_year,
            'get_interest_received':self._get_interest_received,
            'get_interest_received_last_year':self._get_interest_received_last_year,
            'get_Gain_loss_on_foreign_exchange' :self._get_Gain_loss_on_foreign_exchange,
            'get_Gain_loss_on_foreign_exchange_last_year' :self._get_Gain_loss_on_foreign_exchange_last_year,
            'get_prior_adu':self._get_prior_adu,
            'get_prior_adu_last_year':self._get_prior_adu_last_year,
            'get_inventory':self._get_inventory, 
            'get_inventory_last_year':self._get_inventory_last_year, 
            'get_work_in_progress':self._get_work_in_progress,
            'get_work_in_progress_last_year':self._get_work_in_progress_last_year,
            'get_trade_receivables':self._get_trade_receivables,
            'get_trade_receivables_last_year':self._get_trade_receivables_last_year,
            'get_other_receivables':self._get_other_receivables,
            'get_other_receivables_last_year':self._get_other_receivables_last_year,
            'get_trade_payables' : self._get_trade_payables,
            'get_trade_payables_last_year' : self._get_trade_payables_last_year,
            'get_other_payables':self._get_other_payables,
            'get_other_payables_last_year':self._get_other_payables_last_year,
            'get_project_advance_payment':self._get_project_advance_payment,
            'get_project_advance_payment_last_year':self._get_project_advance_payment_last_year,
            'get_taxation':self._get_taxation,
            'get_taxation_last_year':self._get_taxation_last_year,
            'get_interest' : self._get_interest,
            'get_interest_last_year' : self._get_interest_last_year,
            'get_property_plan':self._get_property_plan, 
            'get_property_plan_last_year':self._get_property_plan_last_year, 
            'get_dividend_received' : self._get_dividend_received,
            'get_dividend_received_last_year' : self._get_dividend_received_last_year,
            'get_issue_share_capi': self._get_issue_share_capi,
            'get_issue_share_capi_last_year': self._get_issue_share_capi_last_year,
            'get_borrowing': self._get_borrowing,
            'get_borrowing_last_year': self._get_borrowing_last_year,
            'get_dividend_paid': self._get_dividend_paid,
            'get_dividend_paid_last_year': self._get_dividend_paid_last_year,
            'get_cash_generated_before_changes_in_working_capital':self._get_cash_generated_before_changes_in_working_capital,
            'get_cash_generated_before_changes_in_working_capital_last_year':self._get_cash_generated_before_changes_in_working_capital_last_year,
            'get_cash_flow_from_working_assets': self._get_cash_flow_from_working_assets,
            'get_cash_flow_from_working_assets_last_year': self._get_cash_flow_from_working_assets_last_year,
             
            'get_net_cashflow_from_financing_activities': self._get_net_cashflow_from_financing_activities,
            'get_net_cashflow_from_financing_activities_last_year': self._get_net_cashflow_from_financing_activities_last_year,
            'get_net_cash_flow_from_operating_activities':self._get_net_cash_flow_from_operating_activities,
            'get_net_cash_flow_from_operating_activities_last_year':self._get_net_cash_flow_from_operating_activities_last_year,
            'get_net_cashflow_from_investing_activities': self._get_net_cashflow_from_investing_activities,
            'get_net_cashflow_from_investing_activities_last_year': self._get_net_cashflow_from_investing_activities_last_year,
            'get_cash_and_cash_equivalent_for_the_year': self._get_cash_and_cash_equivalent_for_the_year,
            'get_cash_and_cash_equivalent_for_the_year_last_year': self._get_cash_and_cash_equivalent_for_the_year_last_year,
            'get_cash_bank' : self._get_cash_bank, 
            'get_cash_bank_last_year' : self._get_cash_bank_last_year, 
            'get_closing_balance_of_cash_Equivalents' :self._get_closing_balance_of_cash_Equivalents,
            'get_closing_balance_of_cash_Equivalents_last_year' :self._get_closing_balance_of_cash_Equivalents_last_year
        })
        self.context = context

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
        
        if last_year_ids:
            if data.get('form', False) and data['form'].get('fiscalyear_id', False):
                return datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, last_year_ids[0]).date_stop,'%Y-%m-%d').year
        return ''

    def _get_last_fiscalyear_id(self, data):
        fisc_year = self.pool.get('account.fiscalyear')
        account_period_obj = self.pool.get('account.period')
        date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
        last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
        return last_year_ids[0]

    def _get_balance(self,data,account,year):
        result = {}
        ctx = self.context.copy()
        
        date_start = datetime.strptime(pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_start,'%Y-%m-%d')
        fisc_year = self.pool.get('account.fiscalyear')
        if year=='this':
            ctx['fiscalyear'] = data['form']['fiscalyear_id']
        elif year=='last':
            last_year_date = (date_start- relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
            last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
            if not last_year_ids:
                return 0.0
            ctx['fiscalyear'] = last_year_ids[0]
        elif year=='last_to_last':
            last_year_date = (date_start- relativedelta(years=2)).strftime('%Y-%m-%d %H:%M:%S')
            last_year_ids = fisc_year.search(self.cr, self.uid, [('date_start','=',last_year_date)])
            if not last_year_ids:
                return 0.0
            ctx['fiscalyear'] = last_year_ids[0]
        res_user_obj=self.pool.get('res.users')
        res_data = res_user_obj.browse(self.cr,self.uid,self.uid)
        account_obj = self.pool.get('account.account')
        
        reve_ids = account_obj.search(self.cr, self.uid, [('name', '=',account),('company_id','=',res_data.company_id.id)])
        if reve_ids:
            result = account_obj.read(self.cr, self.uid, reve_ids, ['balance'], ctx)
        else :
            return 0.0
        for amt in result:
            if amt:
                return amt['balance']
            else:
                return 0.0
        
    def _get_profit_loss_before_tax(self, data):
         revanue_amt = self._get_balance(data,'Revenue', 'this')
         other_income_amt = self._get_balance(data, 'Other Income', 'this')
         dir_cost_amt = self._get_balance(data, 'Direct Cost', 'this')
         admin_expe_amt=self._get_balance(data, 'Administrative Expense','this')
         fina_charge_amt = self._get_balance(data, 'Finance Charges', 'this')
         tot_amt = (revanue_amt+other_income_amt) - (dir_cost_amt + admin_expe_amt +fina_charge_amt)
         return tot_amt
     
    def _get_profit_loss_before_tax_last_year(self, data):
         revanue_amt = self._get_balance(data,'Revenue', 'last')
         other_income_amt = self._get_balance(data, 'Other Income', 'last')
         dir_cost_amt = self._get_balance(data, 'Direct Cost', 'last')
         admin_expe_amt=self._get_balance(data, 'Administrative Expense','last')
         fina_charge_amt = self._get_balance(data, 'Finance Charges', 'last')
         tot_amt = (revanue_amt+other_income_amt) - (dir_cost_amt + admin_expe_amt +fina_charge_amt)
         return tot_amt
     
    def _get_depreciation(self, data):
         depr_amt = self._get_balance(data, 'Depreciation', 'this')
         return depr_amt
     
    def _get_depreciation_last_year(self,data):
         depr_amt = self._get_balance(data, 'Depreciation', 'last')
         return depr_amt
         
    def _get_investment(self,data):
         inv_ass_amt_last = self._get_balance(data, 'Investments in Associate', 'last')
         other_invest_last = self._get_balance(data, 'Other Investments', 'last')
         
         inv_ass = self._get_balance(data, 'Investments in Associate', 'this')
         other_inv = self._get_balance(data, 'Other Investments', 'this')
         return ((inv_ass_amt_last + other_invest_last)-(inv_ass + other_inv))

    def _get_investment_last_year(self,data):
        inv_ass_amt_last_to_last = self._get_balance(data, 'Investments in Associate', 'last_to_last')
        other_invest_last_to_last = self._get_balance(data, 'Other Investments', 'last_to_last')
        
        inv_ass_last = self._get_balance(data, 'Investments in Associate', 'this')
        other_invest_last = self._get_balance(data, 'Other Investments', 'this')
        
        return (inv_ass_amt_last_to_last + other_invest_last_to_last) - (inv_ass_last + other_invest_last)
    
    def _get_amortization(self, data):
        return self._get_balance(data, 'Amortization of Intangible Assets', 'this')
    
    def _get_amortization_last_year(self,data):
        amo_amt = self._get_balance(data, 'Amortization of Intangible Assets', 'last')
        return amo_amt
    
    def _get_sale_of_fixed_assets(self, data):
        sale_amt = self._get_balance(data, 'Gain/(Loss) on Sale of Fixed Assets', 'this')
        if sale_amt == None:
            return 0.0
        return sale_amt
    
    def _get_sale_of_fixed_assets_last_year(self,data):
        sale_amt = self._get_balance(data, 'Gain/(Loss) on Sale of Fixed Assets', 'last')
        if sale_amt == None:
            return 0.0
        return self._get_balance(data, 'Gain/(Loss) on Sale of Fixed Assets', 'last')
    
    def _get_interest_received(self,data):
        a = self._get_balance(data, 'Interest Received', 'this')
        return self._get_balance(data, 'Interest Received', 'this')
    
    def _get_interest_received_last_year(self,data):
        if self._get_balance(data, 'Interest Received', 'last')==None:
            return 0.0
        return self._get_balance(data, 'Interest Received', 'last')
    
    def _get_Gain_loss_on_foreign_exchange(self,data):
        if self._get_balance(data, 'Foreign Exchange Gain/Loss', 'this')==None:
            return 0.0
        return self._get_balance(data, 'Foreign Exchange Gain/Loss', 'this')
        
    def _get_Gain_loss_on_foreign_exchange_last_year(self,data):
        return self._get_balance(data, 'Foreign Exchange Gain/Loss', 'last')
    
    def _get_prior_adu(self,data):
        if self._get_balance(data, 'Prior Year Adjustment/Errors', 'this')==None:
            return 0.0
        return self._get_balance(data, 'Prior Year Adjustment/Errors', 'this')
    
    def _get_prior_adu_last_year(self,data):
        return self._get_balance(data, 'Prior Year Adjustment/Errors', 'last')
 
    def _get_inventory(self,data):
        return self._get_balance(data, 'Inventories', 'last') -self._get_balance(data, 'Inventories', 'this')
        
    def _get_inventory_last_year(self,data):
        return self._get_balance(data, 'Inventories', 'last_to_last')-self._get_balance(data, 'Inventories', 'last')
    
    def _get_work_in_progress(self,data):
        if self._get_balance(data, 'Work in Progress', 'last') and self._get_balance(data, 'Work in Progress', 'this'):
            return self._get_balance(data, 'Work in Progress', 'last')-self._get_balance(data, 'Work in Progress', 'this')
        return 0.0
        
    def _get_work_in_progress_last_year(self,data):
        return self._get_balance(data, 'Work in Progress', 'last_to_last')-self._get_balance(data, 'Work in Progress', 'last')
    
    def _get_trade_receivables(self,data):
        return self._get_balance(data, 'Trade Receivables', 'last')-self._get_balance(data, 'Trade Receivables', 'this')
        
    def _get_trade_receivables_last_year(self,data):
        return self._get_balance(data, 'Trade Receivables', 'last_to_last')-self._get_balance(data, 'Trade Receivables', 'last')
    
    def _get_other_receivables(self,data):
        return self._get_balance(data, 'Other Receivables', 'last')-self._get_balance(data, 'Other Receivables', 'this')
        
    def _get_other_receivables_last_year(self,data):
        return self._get_balance(data, 'Other Receivables', 'last_to_last')-self._get_balance(data, 'Other Receivables', 'last')
    
    def _get_trade_payables(self,data):
        return self._get_balance(data, 'Trade Payables', 'this')-self._get_balance(data, 'Trade Payables', 'last')
        
    def _get_trade_payables_last_year(self,data):
        return self._get_balance(data, 'Trade Payables', 'last')-self._get_balance(data, 'Trade Payables', 'last_to_last')
        
    def _get_other_payables(self,data):
        return self._get_balance(data, 'Other Payables', 'this')-self._get_balance(data, 'Other Payables', 'last')
        
    def _get_other_payables_last_year(self,data):
        return self._get_balance(data, 'Other Payables', 'last')-self._get_balance(data, 'Other Payables', 'last_to_last')
    
    def _get_project_advance_payment(self,data):
        this_year_amt = self._get_balance(data, 'Project Advances (Long Term)', 'this') + self._get_balance(data, 'Project Advances (Short Term)', 'this')
        last_year_amt = self._get_balance(data, 'Project Advances (Long Term)', 'last') + self._get_balance(data, 'Project Advances (Short Term)', 'last')
        return this_year_amt - last_year_amt
  
    def _get_project_advance_payment_last_year(self,data):
        last_year_amt = self._get_balance(data, 'Project Advances (Long Term)', 'last') + self._get_balance(data, 'Project Advances (Short Term)', 'last')
        last_last_year_amt = self._get_balance(data, 'Project Advances (Long Term)', 'last_to_last') + self._get_balance(data, 'Project Advances (Short Term)', 'last_to_last')
        return last_year_amt - last_last_year_amt
    
    def _get_taxation(self,data):
        if self._get_balance(data, 'Taxation', 'last') and self._get_balance(data, 'Taxation', 'this') and self._get_balance(data, 'Corporate Tax', 'this'):
            return (self._get_balance(data, 'Taxation', 'last') - self._get_balance(data, 'Taxation', 'this')) + self._get_balance(data, 'Corporate Tax', 'this')
        return 0.0
    def _get_taxation_last_year(self,data):
        return (self._get_balance(data, 'Taxation', 'last_to_last') - self._get_balance(data, 'Taxation', 'last')) + self._get_balance(data, 'Corporate Tax', 'last')
    
    def _get_interest(self,data):
            return self._get_balance(data, 'Interest', 'this')
         
    def _get_interest_last_year(self,data):
        return self._get_balance(data, 'Interest', 'last') 
    
    def _get_property_plan(self,data):
        return self._get_balance(data, 'Property Plant & Equipment', 'this')-self._get_balance(data, 'Property Plant & Equipment', 'last')
     
    def _get_property_plan_last_year(self,data):
       return self._get_balance(data, 'Property Plant & Equipment', 'last')-self._get_balance(data, 'Property Plant & Equipment', 'last_to_last')
        
 
    
    def _get_dividend_received(self,data):
        return self._get_balance(data, 'Dividend Received', 'this')
     
    def _get_dividend_received_last_year(self,data):
        if self._get_balance(data, 'Dividend Received', 'last') ==None:
            return 0.0
        return self._get_balance(data, 'Dividend Received', 'last') 
    
    
    def _get_issue_share_capi(self,data):
        return self._get_balance(data, 'Issue Of Share Capital', 'this')
         
    def _get_issue_share_capi_last_year(self,data):
        return self._get_balance(data, 'Issue Of Share Capital', 'last') 
    
    def _get_borrowing(self, data):
        this_boro = self._get_balance(data, 'Long Term Borrowings', 'this') + self._get_balance(data, 'Short Term Borrowings', 'this')
        last_boro = self._get_balance(data, 'Long Term Borrowings', 'last') + self._get_balance(data, 'Short Term Borrowings', 'last')
        return this_boro-last_boro
    
    def _get_borrowing_last_year(self,data):
        last_to_last_boro = self._get_balance(data, 'Long Term Borrowings', 'last_to_last') + self._get_balance(data, 'Short Term Borrowings', 'last_to_last')
        last_boro = self._get_balance(data, 'Long Term Borrowings', 'last') + self._get_balance(data, 'Short Term Borrowings', 'last')
        return last_boro-last_to_last_boro 
  
    def _get_dividend_paid(self,data):
        return self._get_balance(data, 'Dividends Paid', 'this')
     
    def _get_dividend_paid_last_year(self,data):
            return self._get_balance(data, 'Dividends Paid', 'last') 
        
    def _get_cash_generated_before_changes_in_working_capital(self,data):
      return (self._get_depreciation(data) 
        + self._get_investment(data) 
        + self._get_amortization(data) 
        + self._get_sale_of_fixed_assets(data)+ self._get_interest_received(data)
        + self._get_Gain_loss_on_foreign_exchange(data)+ self._get_prior_adu(data))
#               
    def _get_cash_generated_before_changes_in_working_capital_last_year(self,data):
        return (self._get_depreciation_last_year(data) 
        + self._get_investment_last_year(data) 
        + self._get_amortization_last_year(data) 
        + self._get_sale_of_fixed_assets_last_year(data)+ self._get_interest_received_last_year(data)
        + self._get_Gain_loss_on_foreign_exchange_last_year(data)+ self._get_prior_adu_last_year(data))
        
    def _get_cash_flow_from_working_assets(self,data):
         return (self._get_inventory(data)+ 
               self._get_work_in_progress(data)+
               self._get_trade_receivables(data)+
               self._get_other_receivables(data)+
               self._get_trade_payables(data)+
               self._get_other_payables(data)+
               self._get_project_advance_payment(data)+
               self._get_taxation(data)+
               self._get_interest(data))
    
    def _get_net_cashflow_from_investing_activities_last_year(self,data):
        return (self._get_property_plan_last_year(data)+
        self._get_sale_of_fixed_assets_last_year(data)+
        self._get_interest_received_last_year(data)+
        self._get_dividend_received_last_year(data))
        
    def _get_net_cashflow_from_financing_activities(self,data):
        return (self._get_issue_share_capi(data)+
                 self._get_trade_payables(data)+
                   self._get_other_payables(data)+
                   self._get_project_advance_payment(data)+
                   self._get_taxation(data)+
                   self._get_interest(data))
                   
    def _get_cash_flow_from_working_assets_last_year(self,data):
        return (self._get_inventory_last_year(data)+ 
               self._get_work_in_progress_last_year(data)+
               self._get_trade_receivables_last_year(data)+
               self._get_other_receivables_last_year(data)+
               self._get_trade_payables_last_year(data)+
               self._get_other_payables_last_year(data)+
               self._get_project_advance_payment_last_year(data)+
               self._get_taxation_last_year(data)+
               self._get_interest_last_year(data))
          
    def _get_net_cash_flow_from_operating_activities(self,data):     
               return self._get_cash_generated_before_changes_in_working_capital(data) + self._get_cash_flow_from_working_assets(data)
       
    def _get_net_cash_flow_from_operating_activities_last_year(self,data):     
               return self._get_cash_generated_before_changes_in_working_capital_last_year(data) + self._get_cash_flow_from_working_assets_last_year(data)
           
    def _get_net_cashflow_from_investing_activities(self,data):
            return (self._get_property_plan(data)+
            self._get_sale_of_fixed_assets(data)+
            self._get_interest_received(data)+
            self._get_dividend_received(data))
                        
    def _get_net_cashflow_from_investing_activities_last_year(self,data):
        return (self._get_property_plan_last_year(data)+
        self._get_sale_of_fixed_assets_last_year(data)+
        self._get_interest_received_last_year(data)+
        self._get_dividend_received_last_year(data))
        
    def _get_net_cashflow_from_financing_activities(self,data):
        return (self._get_issue_share_capi(data)+
                self._get_borrowing(data)+
                    self._get_interest(data)+
                    self._get_dividend_paid(data))
    
    def _get_net_cashflow_from_financing_activities_last_year(self,data):
        return (self._get_issue_share_capi_last_year(data)+
                self._get_borrowing_last_year(data)+
                self._get_interest_last_year(data)+
                self._get_dividend_paid_last_year(data))
   
    def _get_cash_and_cash_equivalent_for_the_year(self,data):
        return (self._get_net_cash_flow_from_operating_activities(data)+
                self._get_net_cashflow_from_investing_activities(data)+
                self._get_net_cashflow_from_financing_activities(data))
        
    def _get_cash_and_cash_equivalent_for_the_year_last_year(self,data):
        return (self._get_net_cash_flow_from_operating_activities_last_year(data)+
                self._get_net_cashflow_from_investing_activities_last_year(data)+
                self._get_net_cashflow_from_financing_activities_last_year(data))
   
    def _get_cash_bank(self,data):
        return self._get_balance(data, 'Bank & Cash', 'this')
     
    def _get_cash_bank_last_year(self,data):
        return self._get_balance(data, 'Bank & Cash', 'last') 
        
    def _get_closing_balance_of_cash_Equivalents(self,data):
        return self._get_cash_bank(data)+ self._get_cash_and_cash_equivalent_for_the_year(data)
    
    def _get_closing_balance_of_cash_Equivalents_last_year(self,data):
        return self._get_cash_bank_last_year(data)+ self._get_cash_and_cash_equivalent_for_the_year_last_year(data)

        
report_sxw.report_sxw('report.cash.flow.statement', 'account.account', 'addons/ifrs_account_report/report/cash_flow_statement.rml', parser=cash_flow_statement, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
