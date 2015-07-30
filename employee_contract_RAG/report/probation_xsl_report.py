# -*- coding: utf-8 -*-
# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.

from __future__ import division

import xlwt
import time
#import account_financial_report_webkit
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
#from openerp.addons.account_financial_report_webkit.report.aged_partner_balance import AccountAgedTrialBalanceWebkit
from openerp.addons.employee_contract_RAG.report.probation_report import request
from openerp.tools.translate import _

from openerp import pooler
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

def make_ranges(top, offset):
    """Return sorted days ranges

    :param top: maximum overdue day
    :param offset: offset for ranges

    :returns: list of sorted ranges tuples in days
              eg. [(-100000, 0), (0, offset), (offset, n*offset), ... (top, 100000)]
    """
    ranges = [(n, min(n + offset, top)) for n in xrange(0, top, offset)]
    ranges.insert(0, (-100000000000, 0))
    ranges.append((top, 100000000000))
    return ranges

#list of overdue ranges
RANGES = make_ranges(120, 30)


def make_ranges_titles():
    """Generates title to be used by mako"""
    titles = [_('Not Due')]
    titles += [_(u'Overdue ≤ %s d.') % x[1] for x in RANGES[1:-1]]
    titles.append(_('Older'))
    return titles

#list of overdue ranges title
RANGES_TITLES = make_ranges_titles()

#list of payable journal types
REC_PAY_TYPE = ('purchase', 'sale')
#list of refund payable type

REFUND_TYPE = ('purchase_refund', 'sale_refund')

INV_TYPE = REC_PAY_TYPE + REFUND_TYPE
PAYMENT_IDS=[]
PAYMENT_NAMES=[]


class open_invoices_xls(report_xls):
    column_sizes = [12,12,20,15,30,30,14,14,14,14,14,14,10]

    def global_initializations(self, wb, _p, xlwt, _xs, objects, data):
        # this procedure will initialise variables and Excel cell styles and return them as global ones
        global ws
        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']
        #-------------------------------------------------------
        global nbr_columns  #number of columns is 11 in case of normal report, 13 in case the option currency is selected and 12 in case of the regroup by currency option is checked
        group_lines = False

        if group_lines:
            nbr_columns = 12
        #Relacing This Line................

        #elif _p.amount_currency(data) and not group_lines:
        elif _p.get_currency(data) and not group_lines:
            nbr_columns = 13
        else:
            nbr_columns = 11
        #-------------------------------------------------------
        global style_font12  #cell style for report title
        style_font12 = xlwt.easyxf(_xs['xls_title'])
        #-------------------------------------------------------
        global style_default
        style_default = xlwt.easyxf(_xs['borders_all'])
        #-------------------------------------------------------
        global style_default_italic
        style_default_italic = xlwt.easyxf(_xs['borders_all'] + _xs['italic'])
        #-------------------------------------------------------
        global style_bold
        style_bold = xlwt.easyxf(_xs['bold'] + _xs['borders_all'])
        #-------------------------------------------------------
        global style_bold_center
        style_bold_center = xlwt.easyxf(_xs['bold'] + _xs['borders_all'] + _xs['center'])
        #-------------------------------------------------------
        global style_bold_italic
        style_bold_italic = xlwt.easyxf(_xs['bold'] + _xs['borders_all'] + _xs['italic'])
        #-------------------------------------------------------
        global style_bold_italic_decimal
        style_bold_italic_decimal = xlwt.easyxf(_xs['bold'] + _xs['borders_all'] + _xs['italic'] + _xs['right'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_bold_blue
        style_bold_blue = xlwt.easyxf(_xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] )
        #-------------------------------------------------------
        global style_bold_blue_italic_decimal
        style_bold_blue_italic_decimal = xlwt.easyxf(_xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] + _xs['italic'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_bold_blue_center #cell style for header titles: 'Chart of accounts' - 'Fiscal year' ...
        style_bold_blue_center= xlwt.easyxf(_xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] + _xs['center'])
        #-------------------------------------------------------
        global style_center #cell style for header data: 'Chart of accounts' - 'Fiscal year' ...
        style_center = xlwt.easyxf(_xs['borders_all'] + _xs['wrap'] + _xs['center'])
        #-------------------------------------------------------
        global style_yellow_bold #cell style for columns titles 'Date'- 'Period' - 'Entry'...
        style_yellow_bold = xlwt.easyxf(_xs['bold'] + _xs['fill'] + _xs['borders_all'])
        #-------------------------------------------------------
        global style_yellow_bold_right #cell style for columns titles 'Date'- 'Period' - 'Entry'...
        style_yellow_bold_right = xlwt.easyxf(_xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs['right'])
        #-------------------------------------------------------
        global style_right
        style_right = xlwt.easyxf(_xs['borders_all'] + _xs['right'])
        #-------------------------------------------------------
        global style_right_italic
        style_right_italic = xlwt.easyxf(_xs['borders_all'] + _xs['right'] + _xs['italic'])
        #-------------------------------------------------------
        global style_decimal
        style_decimal = xlwt.easyxf(_xs['borders_all'] + _xs['right'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_decimal_italic
        style_decimal_italic = xlwt.easyxf(_xs['borders_all'] + _xs['right'] + _xs['italic'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_date
        style_date = xlwt.easyxf(_xs['borders_all'] + _xs['left'], num_format_str = report_xls.date_format)
        #-------------------------------------------------------
        global style_date_italic
        style_date_italic = xlwt.easyxf(_xs['borders_all'] + _xs['left'] + _xs['italic'], num_format_str = report_xls.date_format)
        #-------------------------------------------------------
        global style_account_title, style_account_title_right, style_account_title_decimal
        cell_format = _xs['xls_title'] + _xs['bold'] + _xs['fill'] + _xs['borders_all']
        style_account_title = xlwt.easyxf(cell_format)
        style_account_title_right = xlwt.easyxf(cell_format + _xs['right'])
        style_account_title_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_partner_row
        cell_format = _xs['bold']
        style_partner_row = xlwt.easyxf(cell_format)
        #-------------------------------------------------------
        global style_partner_cumul, style_partner_cumul_right, style_partner_cumul_center, style_partner_cumul_decimal
        cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        style_partner_cumul = xlwt.easyxf(cell_format)
        style_partner_cumul_right = xlwt.easyxf(cell_format + _xs['right'])
        style_partner_cumul_center = xlwt.easyxf(cell_format + _xs['center'])
        style_partner_cumul_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str = report_xls.decimal_format)

    def print_title(self, _p, row_position): # print the first line "OPEN INVOICE REPORT - db name - Currency
        report_name =  ' - '.join([_p.report_name.upper(), _p.company.partner_id.name, _p.company.currency_id.name])
        c_specs = [('report_name', nbr_columns, 0, 'text', report_name), ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, row_style=style_font12)
        return row_position

    def print_empty_row(self, row_position): #send an empty row to the Excel document
        c_sizes = self.column_sizes
        c_specs = [('empty%s'%i, 1, c_sizes[i], 'text', None) for i in range(0,len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, set_column_size=True)
        return row_position

    def print_header_titles(self, _p, data, row_position): #Fill in the titles of the header summary tables: Chart of account - Fiscal year - ...
        c_specs = [
            ('coa', 2, 0, 'text', _('Chart of Account'), None, style_bold_blue_center),
            ('fy', 2, 0, 'text', _('Fiscal Year'), None, style_bold_blue_center),
            ('df', 2, 0, 'text', _p.filter_form(data) == 'filter_date' and _('Dates Filter') or _('Periods Filter'), None, style_bold_blue_center),
            ('cd', 1 if nbr_columns == 11 else 2 , 0, 'text', _('Clearance Date'), None, style_bold_blue_center),
            ('af', 2, 0, 'text', _('Accounts Filter'), None, style_bold_blue_center),
            ('tm', 3 if nbr_columns == 13 else 2, 0, 'text', _('Target Moves'), None, style_bold_blue_center),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, row_style=style_bold_blue_center)
        return row_position


    def print_header_data(self, _p, data, row_position):   #Fill in the data of the header summary tables: Chart of account - Fiscal year - ...
        c_specs = [
            ('coa', 2, 0, 'text', _p.chart_account.name, None, style_center),
            ('fy', 2, 0, 'text', _p.fiscalyear.name if _p.fiscalyear else '-', None, style_center),
        ]
        df = _('From') + ': '
        if _p.filter_form(data) == 'filter_date':
            df += _p.start_date if _p.start_date else u''
        else:
            df += _p.start_period.name if _p.start_period else u''
        df += ' ' + _('To') + ': '
        if _p.filter_form(data) == 'filter_date':
            df += _p.stop_date if _p.stop_date else u''
        else:
            df += _p.stop_period.name if _p.stop_period else u''
        c_specs += [
            ('df', 2, 0, 'text', df, None, style_center),
            ('cd', 1 if nbr_columns == 11 else 2, 0, 'text', _p.date_until, None, style_center), #clearance date
            ('af', 2, 0, 'text', _('Custom Filter') if _p.partner_ids else _p.display_partner_account(data), None, style_center),
            ('tm', 3 if nbr_columns == 13 else 2, 0, 'text', _p.display_target_move(data), None, style_center),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, row_style=style_center)
        return row_position

    def print_columns_title(self, _p, data, row_position):  # Fill in a row with the titles of the columns for the invoice lines: Date - Period - Entry -...


        c_specs = [
        ('staff', 1, 0, 'text', _('Staff No.'),None,style_yellow_bold),
        ('emp', 1, 0, 'text', _('Employee'),None,style_yellow_bold),
        ('des', 1, 0, 'text',_('Designation'),None,style_yellow_bold),
        ('dep', 1, 0, 'text',_('Department'),None,style_yellow_bold),
        ('emp_date', 1, 0, 'text',_('Employment Date'),None,style_yellow_bold),
        ('prob_start_date', 1, 0, 'text',_('Probation Start Date'),None,style_yellow_bold),
        ('mid_prob_date', 1, 0, 'text',_('Mid-Probation Date'),None,style_yellow_bold),
        ('prob_end_date', 1, 0, 'text', _('Probation End Date'),None,style_yellow_bold),
        ('mid_prob_date', 1, 0, 'text',_('Confirmation Date'),None,style_yellow_bold),
        ('prob_end_date', 1, 0, 'text', _('Benefits Upon Confirmation'),None,style_yellow_bold),
        
        ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, row_style=style_yellow_bold)
        return row_position

    def print_row_code_account(self,account, row_position, partner_name): # Fill in a row with the code and the name of an account + the partner name in case of currency regrouping
        c_specs = [ ('acc_title', nbr_columns, 0, 'text', ' - '.join([account.code, account.name])),  ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, style_account_title)
        return row_position+1

    def print_row_partner(self, row_position, partner_name):
        c_specs = [ ('partner', nbr_columns, 0, 'text', partner_name or _('No partner')),  ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, style_partner_row)
        return row_position

    def print_group_currency(self, row_position, curr, _p):
        c_specs = [ ('curr', nbr_columns, 0, 'text', curr or _p.company.currency_id.name),  ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, style_bold)
        return row_position

    def print_lines(self, row_position, account, line,_p, data, line_number): # Fill in rows of invoice line
        # Mako: <div class="act_as_row lines ${line.get('is_from_previous_periods') and 'open_invoice_previous_line' or ''} ${line.get('is_clearance_line') and 'clearance_line' or ''}">
        if line.get('is_from_previous_periods') or line.get('is_clearance_line'):
            style_line_default = style_default_italic
            style_line_right = style_right_italic
            style_line_date = style_date_italic
            style_line_decimal = style_decimal_italic
        else:
            style_line_default = style_default
            style_line_right = style_right
            style_line_date = style_date
            style_line_decimal = style_decimal

        c_specs = [
                    ]

        row_data = self.xls_row_template(c_specs)
        row_position = self.xls_write_row(ws, row_position, row_data, style_line_default)
        return row_position


    def compute_aged_lines(self, partner_id, ledger_lines, data):
        """Add property aged_lines to accounts browse records

        contained in :attr:`objects` for a given partner

        :param: partner_id: current partner
        :param ledger_lines: generated by parent
                 :class:`.open_invoices.PartnersOpenInvoicesWebkit`

        :returns: dict of computed aged lines
                  eg {'balance': 1000.0,
                       'aged_lines': {(90, 120): 0.0, ...}

        """

        #print "Here is the Payment Term in Data Hope It Exists Here:::",data

        lines_to_age = self.filter_lines(partner_id, ledger_lines)
        res = {}
        end_date = self._get_end_date(data)
        aged_lines = dict.fromkeys(RANGES, 0.0)
        reconcile_lookup = self.get_reconcile_count_lookup(lines_to_age)
        res['aged_lines'] = aged_lines
        for line in lines_to_age:
            compute_method = self.get_compute_method(reconcile_lookup,
                                                     partner_id,
                                                     line)
            delay = compute_method(line, end_date, ledger_lines)
            classification = self.classify_line(partner_id, delay)
            aged_lines[classification] += line['debit'] - line['credit']
            #print "aged_lines in XLS:::::::", aged_lines

        self.compute_balance(res, aged_lines)

        return res

    def _get_end_date(self, data):
        """Retrieve end date to be used to compute delay.

        :param data: data dict send to report contains form dict

        :returns: end date to be used to compute overdue delay

        """
        end_date = None
        date_to = data['form']['date_to']
        period_to_id = data['form']['period_to']
        fiscal_to_id = data['form']['fiscalyear_id']
        if date_to:
            end_date = date_to
        elif period_to_id:
            period_to = self.pool['account.period'].browse(self.cr,
                                                           self.uid,
                                                           period_to_id)
            end_date = period_to.date_stop
        elif fiscal_to_id:
            fiscal_to = self.pool['account.fiscalyear'].browse(self.cr,
                                                               self.uid,
                                                               fiscal_to_id)
            end_date = fiscal_to.date_stop
        else:
            raise ValueError('End date and end period not available')

        return end_date

    def get_compute_method(self, reconcile_lookup, partner_id, line):
        """Get the function that should compute the delay for a given line

        :param reconcile_lookup: dict of reconcile group by id and count
                                 {rec_id: count of line related to reconcile}
        :param partner_id: current partner_id
        :param line: current ledger line generated by parent
                     :class:`.open_invoices.PartnersOpenInvoicesWebkit`

        :returns: function bounded to :class:`.AccountAgedTrialBalanceWebkit`

        """
        if reconcile_lookup.get(line['rec_id'], 0.0) > 1:
            #print "reconcile_lookup details :::::::",reconcile_lookup
            return self.compute_delay_from_partial_rec
        elif line['jtype'] in INV_TYPE and line.get('date_maturity'):
            return self.compute_delay_from_maturity
        else:
            return self.compute_delay_from_date

    def line_is_valid(self, partner_id, line):
        """Predicate hook that allows to filter line to be treated

        :param partner_id: current partner_id
        :param line: current ledger line generated by parent
                     :class:`.open_invoices.PartnersOpenInvoicesWebkit`

        :returns: boolean True if line is allowed
        """
        #print "NUMBER-----14"
        return True

    def filter_lines(self, partner_id, lines):
        """Filter ledger lines that have to be treated

        :param partner_id: current partner_id
        :param lines: ledger_lines related to current partner
                      and generated by parent
                      :class:`.open_invoices.PartnersOpenInvoicesWebkit`

        :returns: list of allowed lines

        """
        #print "[x for x in lines if self.line_is_valid(partner_id, x)]=====15"
        return [x for x in lines if self.line_is_valid(partner_id, x)]

    def classify_line(self, partner_id, overdue_days):
        """Return the overdue range for a given delay

        We loop from smaller range to higher
        This should be the most effective solution as generaly
        customer tend to have one or two month of delay

        :param overdue_days: delay in days
        :param partner_id: current partner_id

        :returns: the correct range in :const:`RANGES`

        """
        for drange in RANGES:
            if overdue_days <= drange[1]:
                return drange
        return drange

    def compute_balance(self, res, aged_lines):
        """Compute the total balance of aged line
        for given account"""
        res['balance'] = sum(aged_lines.values())
        #print "NUMBER-----17"

    def compute_totals(self, aged_lines):
        """Compute the totals for an account

        :param aged_lines: dict of aged line taken from the
                           property added to account record

        :returns: dict of total {'balance':1000.00, (30, 60): 3000,...}

        """
        totals = {}
        totals['balance'] = sum(x.get('balance', 0.0) for
                                x in aged_lines)
        aged_ranges = [x.get('aged_lines', {}) for x in aged_lines]
        for drange in RANGES:
            totals[drange] = sum(x.get(drange, 0.0) for x in aged_ranges)

        return totals

    def compute_percents(self, totals):
        percents = {}
        base = totals['balance'] or 1.0
        for drange in RANGES:

            percents[drange] = (totals[drange] / base) * 100.0

        return percents

    def get_reconcile_count_lookup(self, lines):
        """Compute an lookup dict

        It contains has partial reconcile id as key and the count of lines
        related to the reconcile id

        :param: a list of ledger lines generated by parent
                :class:`.open_invoices.PartnersOpenInvoicesWebkit`

        :retuns: lookup dict {ṛec_id: count}

        """

        l_ids = tuple(x['id'] for x in lines)
        #print "values in l-ids in the aged partner::::::",l_ids
        sql = ("SELECT reconcile_partial_id, COUNT(*) FROM account_move_line"
               "   WHERE reconcile_partial_id IS NOT NULL"
               "   AND id in %s"
               "   GROUP BY reconcile_partial_id")
        self.cr.execute(sql, (l_ids,))
        res = self.cr.fetchall()
        #print "Res values in the aged partner::::::::20"
        return dict((x[0], x[1]) for x in res)


    def print_group_cumul_account(self,row_position, row_start_account, acc):
        #print by account the totals of the credit and debit + balance calculation
        #This procedure will create  an Excel sumif function that will check in the column "label" for the "Cumulated Balance.." string and make a sum of the debit & credit data
        start_col = 4   #the text "Cumulated Balance on Partner starts in column 4 when selecting the option regroup by currency, 5 in  the other case

        c_specs = [

            ('partner_name', 1, 0, 'text',_('Total') ),
            ('invoice_no', 1, 0, 'text', None ),
            ('due',1,0,'number',acc.aged_totals[(-100000000000, 0)]  or 0.0, None,style_account_title_decimal),
            ('od30',1,0,'number',acc.aged_totals[(0, 30)]  or 0.0, None,style_account_title_decimal),
            ('od60',1,0,'number',acc.aged_totals[(30, 60)]  or 0.0, None,style_account_title_decimal),
            ('od90',1,0,'number',acc.aged_totals[(60, 90)]  or 0.0, None,style_account_title_decimal),
            ('od120',1,0,'number',acc.aged_totals[(90, 120)]  or 0.0, None,style_account_title_decimal),
            ('older',1,0,'number',acc.aged_totals[(120, 100000000000)]  or 0.0, None,style_account_title_decimal),
            ('balance', 1, 0, 'number', acc.aged_totals['balance']  or 0.0, None, style_account_title_decimal),
        ]


        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data,style_account_title)
        return row_position+1


    def print_ledger_lines(self, row_pos, lines_data, _xs, xlwt, _p, data): # export the invoice AR/AP lines

            row_start_account = row_pos

            row_start_account = row_pos
            res_obj = self.pool.get('ir.property')

            row_pos = self.print_empty_row(row_pos)
            row_pos = self.print_columns_title(_p, data, row_pos)

            line_number=1
            for acc in lines_data:
                line_number = 0
                balance=0
                line={}
                line['balance'] = acc['total']
                line['partner_name'] = acc['name']
                line['payment_term']=acc['payment_term']        #data['form']['payment_info'][p_id]['payment_term']
                line['due']= acc['direction']
                line['od30']= acc[str(4)]
                line['od60']= acc[str(3)]
                line['od90']= acc[str(2)]
                line['od120']= acc[str(1)]
                line['older']= acc[str(0)]
                line['payment_next_Action_date']=acc['next_action']  #data['form']['payment_info'][p_id]['payment_next_Action_date']
                line['payment_note']=acc['comments'] #data['form']['payment_info'][p_id]['payment_note']
                row_pos_start = row_pos
                row_pos = self.print_lines(row_pos, acc, line, _p, data, line_number)
                line_number += 1

            return row_pos


        ########### Printing Multi Select Values .................
    def _get_lines(self,data,form):
        self.total_account = []
        obj_move = self.pool.get('account.move.line')
        ctx = form.get('used_context', {})
        ctx.update({'fiscalyear': False, 'all_fiscalyear': True})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        self.direction_selection = form.get('direction_selection', 'past')
        self.target_move = form.get('target_move', 'all')
        self.date_from = form.get('date_from', time.strftime('%Y-%m-%d'))
        if (form['result_selection'] == 'customer' ):
            self.ACCOUNT_TYPE = ['receivable']
        elif (form['result_selection'] == 'supplier'):
            self.ACCOUNT_TYPE = ['payable']
        else:
            self.ACCOUNT_TYPE = ['payable','receivable']

        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']

        # Checking Multiple Payment Terms that Any Null customers with payment term Ids

        if len(form['payment_term_id']) > 1:    
            for val in form['multi'].keys():
                if 'partner_id' in form['multi'][val].keys():
                    partners_list=form['multi'][val]['partner_id']            

                    self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
                        res_partner.name AS name \
                        FROM res_partner,account_move_line AS l, account_account, account_move am\
                        WHERE (l.account_id=account_account.id) \
                        AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND account_account.active\
                        AND ((reconcile_id IS NULL)\
                        OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND (l.partner_id=res_partner.id)\
                        AND (l.date <= %s)\
                        AND ' + self.query + ' \
                        AND (res_partner.id IN %s)\
                        ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,tuple(partners_list)))

                    partners = self.cr.dictfetchall()
                    if partners:
                        pass
                    else:
                        del form['multi'][val]
                else:
                    del form['multi'][val]

        for val in form['multi'].keys():
            partners=""
            if 'partner_id' in form['multi'][val].keys():
                partners_list= form['multi'][val]['partner_id']
                payment_name=form['multi'][val]['payment_name']
            # Added New customized Sql Query............

                self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name \
                    FROM res_partner,account_move_line AS l, account_account, account_move am\
                    WHERE (l.account_id=account_account.id) \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND account_account.active\
                    AND ((reconcile_id IS NULL)\
                    OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND (l.partner_id=res_partner.id)\
                    AND (l.date <= %s)\
                    AND ' + self.query + ' \
                    AND (res_partner.id IN %s)\
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,tuple(partners_list)))

                partners = self.cr.dictfetchall()
            ## mise a 0 du total
            for i in range(7):
                self.total_account.append(0)
            #
            # Build a string like (1,2,3) for easy use in SQL query
            partner_ids = [x['id'] for x in partners]

            if not partner_ids:
                return []

            # This dictionary will store the debit-credit for all partners, using partner_id as key.
            totals = {}

            #self.query=""
            self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND (l.partner_id IN %s)\
                    AND ((l.reconcile_id IS NULL)\
                    OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND ' + self.query + '\
                    AND account_account.active\
                    AND (l.date <= %s)\
                    GROUP BY l.partner_id ', (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
            t = self.cr.fetchall()
            for i in t:
                totals[i[0]] = i[1]

            # This dictionary will store the future or past of all partners
            future_past = {}
            if self.direction_selection == 'future':
                self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity, l.date) < %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
                t = self.cr.fetchall()
                for i in t:
                    future_past[i[0]] = i[1]
            elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
         #       print "Omme Working on Analysis Direction::"
                self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity,l.date) > %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
                t = self.cr.fetchall()
                for i in t:
                    future_past[i[0]] = i[1]

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
            history = []
            for i in range(5):
                args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
                dates_query = '(COALESCE(l.date_maturity,l.date)'

                # Relaced form variable with form['multi'][val]
                if form['multi'][val]['period'][str(i)]['start'] and form['multi'][val]['period'][str(i)]['stop']:
                    dates_query += ' BETWEEN %s AND %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'], form['multi'][val]['period'][str(i)]['stop'])
                elif form['multi'][val]['period'][str(i)]['start']:
                    dates_query += ' > %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'],)
                else:
                    dates_query += ' < %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['stop'],)
                args_list += (self.date_from,)
                self.cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit)
                        FROM account_move_line AS l, account_account, account_move am
                        WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                            AND (am.state IN %s)
                            AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    GROUP BY l.partner_id''', args_list)
                t = self.cr.fetchall()
                d = {}
                for i in t:
                    d[i[0]] = i[1]
                history.append(d)

            for partner in partners:

                values = {}
            ## If choise selection is in the future
                if self.direction_selection == 'future':
                # Query here is replaced by one query which gets the all the partners their 'before' value
                    before = False
                    if future_past.has_key(partner['id']):
                        before = [ future_past[partner['id']] ]
                        self.total_account[6] = self.total_account[6] + (before and before[0] or 0.0)
                        values['direction'] = before and before[0] or 0.0
                elif self.direction_selection == 'past': # Changed this so people could in the future create new direction_selections
                # Query here is replaced by one query which gets the all the partners their 'after' value
                    after = False
                    if future_past.has_key(partner['id']): # Making sure this partner actually was found by the query
                        after = [ future_past[partner['id']] ]

                    self.total_account[6] = self.total_account[6] + (after and after[0] or 0.0)
                    values['direction'] = after and after[0] or 0.0

                for i in range(5):
                    during = False
                    if history[i].has_key(partner['id']):
                        during = [ history[i][partner['id']] ]
                # Ajout du compteur
                    self.total_account[(i)] = self.total_account[(i)] + (during and during[0] or 0)
                    values[str(i)] = during and during[0] or 0.0
                total = False
                if totals.has_key( partner['id'] ):
                    total = [ totals[partner['id']] ]
                values['total'] = total and total[0] or 0.0
            ## Add for total
                self.total_account[(i+1)] = self.total_account[(i+1)] + (total and total[0] or 0.0)
                values['name'] = partner['name']
                id=partner['id']
                values['payment_term']=payment_name
                # Query to Return the Comments and Next action date from res_partner
                self.cr.execute('select payment_note,payment_next_action_date from res_partner where id=%s'%partner['id'])
                comments=self.cr.dictfetchall()[0]
                values['comments']=comments['payment_note']
                values['next_action']=comments['payment_next_action_date']
                res.append(values)

            total = 0.0
            totals = {}
            for r in res:
                total += float(r['total'] or 0.0)
                for i in range(5)+['direction']:
                    totals.setdefault(str(i), 0.0)
                    totals[str(i)] += float(r[str(i)] or 0.0)

        return res



    def get_lines(self,data,form):
        self.total_account = []
        obj_move = self.pool.get('account.move.line')
        ctx = data['form'].get('used_context', {})
        ctx.update({'fiscalyear': False, 'all_fiscalyear': True})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        self.reverse_sign = data['form'].get('reverse_sign', 'False')        
        self.direction_selection = data['form'].get('direction_selection', 'past')
        self.target_move = data['form'].get('target_move', 'all')
        self.date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        if (data['form']['result_selection'] == 'customer' ):
            self.ACCOUNT_TYPE = ['receivable']
        elif (data['form']['result_selection'] == 'supplier'):
            self.ACCOUNT_TYPE = ['payable']
        else:
            self.ACCOUNT_TYPE = ['payable','receivable']

        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name \
                FROM res_partner,account_move_line AS l, account_account, account_move am\
                WHERE (l.account_id=account_account.id) \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND account_account.active\
                    AND ((reconcile_id IS NULL)\
                       OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND (l.partner_id=res_partner.id)\
                    AND (l.date <= %s)\
                    AND ' + self.query + ' \
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,))
        partners = self.cr.dictfetchall()
        ## mise a 0 du total
        for i in range(7):
            self.total_account.append(0)
        #
        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [x['id'] for x in partners]
        if not partner_ids:
            return []
        # This dictionary will store the debit-credit for all partners, using partner_id as key.

        totals = {}
        if self.reverse_sign:
            self.cr.execute('SELECT l.partner_id, SUM(l.credit-l.debit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND ' + self.query + '\
                        AND account_account.active\
                        AND (l.date <= %s)\
                        GROUP BY l.partner_id ', (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
            t = self.cr.fetchall()
        else:
        
            self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND ' + self.query + '\
                        AND account_account.active\
                        AND (l.date <= %s)\
                        GROUP BY l.partner_id ', (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
            t = self.cr.fetchall()
        for i in t:
            totals[i[0]] = i[1]

        # This dictionary will store the future or past of all partners
        future_past = {}
        if self.direction_selection == 'future':
            if self.reverse_sign:        
                self.cr.execute('SELECT l.partner_id, SUM(l.credit-l.debit) \
                            FROM account_move_line AS l, account_account, account_move am \
                            WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                            AND (am.state IN %s)\
                            AND (account_account.type IN %s)\
                            AND (COALESCE(l.date_maturity, l.date) < %s)\
                            AND (l.partner_id IN %s)\
                            AND ((l.reconcile_id IS NULL)\
                            OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                            AND '+ self.query + '\
                            AND account_account.active\
                        AND (l.date <= %s)\
                            GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
                t = self.cr.fetchall()
            else:
        
                self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                            FROM account_move_line AS l, account_account, account_move am \
                            WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                            AND (am.state IN %s)\
                            AND (account_account.type IN %s)\
                            AND (COALESCE(l.date_maturity, l.date) < %s)\
                            AND (l.partner_id IN %s)\
                            AND ((l.reconcile_id IS NULL)\
                            OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                            AND '+ self.query + '\
                            AND account_account.active\
                        AND (l.date <= %s)\
                            GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
                t = self.cr.fetchall()
            for i in t:
                future_past[i[0]] = i[1]
        elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
            if self.reverse_sign:                
                self.cr.execute('SELECT l.partner_id, SUM(l.credit-l.debit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                            AND (am.state IN %s)\
                            AND (account_account.type IN %s)\
                            AND (COALESCE(l.date_maturity,l.date) > %s)\
                            AND (l.partner_id IN %s)\
                            AND ((l.reconcile_id IS NULL)\
                            OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                            AND '+ self.query + '\
                            AND account_account.active\
                        AND (l.date <= %s)\
                            GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
                t = self.cr.fetchall()
            else:                
        
                self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                            AND (am.state IN %s)\
                            AND (account_account.type IN %s)\
                            AND (COALESCE(l.date_maturity,l.date) > %s)\
                            AND (l.partner_id IN %s)\
                            AND ((l.reconcile_id IS NULL)\
                            OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                            AND '+ self.query + '\
                            AND account_account.active\
                        AND (l.date <= %s)\
                            GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
                t = self.cr.fetchall()
            for i in t:
                future_past[i[0]] = i[1]

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
            dates_query = '(COALESCE(l.date_maturity,l.date)'
            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'

                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' > %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' < %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (self.date_from,)
            if self.reverse_sign:                            
                self.cr.execute('''SELECT l.partner_id, SUM(l.credit-l.debit), l.reconcile_partial_id
                        FROM account_move_line AS l, account_account, account_move am 
                        WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                            AND (am.state IN %s)
                            AND (account_account.type IN %s)
                            AND (l.partner_id IN %s)
                            AND ((l.reconcile_id IS NULL)
                              OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                            AND ''' + self.query + '''
                            AND account_account.active
                            AND ''' + dates_query + '''
                        AND (l.date <= %s)
                        GROUP BY l.partner_id, l.reconcile_partial_id''', args_list)
            else:
            
                self.cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit)
                        FROM account_move_line AS l, account_account, account_move am
                        WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                            AND (am.state IN %s)
                            AND (account_account.type IN %s)
                            AND (l.partner_id IN %s)
                            AND ((l.reconcile_id IS NULL)
                              OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                            AND ''' + self.query + '''
                            AND account_account.active
                            AND ''' + dates_query + '''
                        AND (l.date <= %s)
                        GROUP BY l.partner_id''', args_list)
            t = self.cr.fetchall()
            d = {}
            for i in t:
                d[i[0]] = i[1]
            history.append(d)

        for partner in partners:
            values = {}
            ## If choise selection is in the future
            if self.direction_selection == 'future':
                # Query here is replaced by one query which gets the all the partners their 'before' value
                before = False
                if future_past.has_key(partner['id']):
                    before = [ future_past[partner['id']] ]
                self.total_account[6] = self.total_account[6] + (before and before[0] or 0.0)
                values['direction'] = before and before[0] or 0.0
            elif self.direction_selection == 'past': # Changed this so people could in the future create new direction_selections
                # Query here is replaced by one query which gets the all the partners their 'after' value
                after = False
                if future_past.has_key(partner['id']): # Making sure this partner actually was found by the query
                    after = [ future_past[partner['id']] ]

                self.total_account[6] = self.total_account[6] + (after and after[0] or 0.0)
                values['direction'] = after and after[0] or 0.0

            for i in range(5):
                during = False
                if history[i].has_key(partner['id']):
                    during = [ history[i][partner['id']] ]
                # Ajout du compteur
                self.total_account[(i)] = self.total_account[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
            total = False
            if totals.has_key( partner['id'] ):
                total = [ totals[partner['id']] ]
            values['total'] = total and total[0] or 0.0
            ## Add for total
            self.total_account[(i+1)] = self.total_account[(i+1)] + (total and total[0] or 0.0)
            values['name'] = partner['name']

            # Connnect to ir.property table to return the Values for the Payment Term................
            self.cr.execute("select value_reference from ir_property where name='property_payment_term' and res_id='res.partner,%s'    "%partner['id'])
            payment_term_val=self.cr.dictfetchall()
            if payment_term_val:
                payment_term_val=payment_term_val[0]

                self.cr.execute('select name from account_payment_term where id=%s'%payment_term_val['value_reference'].split(',')[-1])
                payment_term = self.cr.dictfetchall()[0]
                values['payment_term']=payment_term['name']
            else:
                values['payment_term']=""
            self.cr.execute('select payment_note,payment_next_action_date from res_partner where id=%s'%partner['id'])
            comments=self.cr.dictfetchall()[0]
            values['comments']=comments['payment_note']
            values['next_action']=comments['payment_next_action_date']
            res.append(values)

        total = 0.0
        totals = {}
        for r in res:
            total += float(r['total'] or 0.0)
            for i in range(5)+['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
        return res


#### Added Functions From Acount Partner Balance................................

    def generate_xls_report(self, _p, _xs, data, objects, wb): # main function
        # Initializations

        _p.update({'report_name':'Probationer Report'})
        
        self.global_initializations(wb,_p, xlwt, _xs, objects, data)
        row_pos = 2

        row_pos = self.print_title(_p, row_pos)

        row_pos = self.print_columns_title(_p, data, row_pos)
        
        ws.set_horz_split_pos(row_pos)




open_invoices_xls('report.personnel_request_xls', 'hr.contract', parser=request)
