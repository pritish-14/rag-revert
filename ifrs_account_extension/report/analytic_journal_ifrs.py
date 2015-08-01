# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

import time
from openerp import pooler
from openerp.report import report_sxw

#
# Use period and Journal for selection or resources
#
class account_analytic_journal(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_analytic_journal, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'time': time,
            'lines': self._lines,
            'lines_a': self._lines_a,
            'sum_general': self._sum_general,
            'sum_analytic': self._sum_analytic,
        })

    def _lines(self, journal_id, date1, date2, account_ids):
        result = []
#        if account_ids:
#            self.cr.execute('SELECT DISTINCT move_id FROM account_analytic_line WHERE (date>=%s) AND (date<=%s) AND (journal_id=%s) AND (move_id is not null) AND (account_id in %s)', (date1, date2, journal_id, ))
#        else:

        self.cr.execute('SELECT DISTINCT move_id FROM account_analytic_line WHERE (date>=%s) AND (date<=%s) AND (journal_id=%s) AND (move_id is not null)', (date1, date2, journal_id))
        ids = map(lambda x: x[0], self.cr.fetchall())
        
        lines = self.pool.get('account.move.line').browse(self.cr, self.uid, ids) or []
        if account_ids:
            for line in lines:
                if line.account_id.id in account_ids:
                    result.append(line)
            return result
        return lines

    def _lines_a(self, move_id, journal_id, date1, date2):
#        if account_ids:
#            ids = self.pool.get('account.analytic.line').search(self.cr, self.uid, [('move_id','=',move_id), ('journal_id','=',journal_id), ('date','>=',date1), ('date','<=',date2)])
#        else:
        print "journal_id:::",journal_id
        ids = self.pool.get('account.analytic.line').search(self.cr, self.uid, [('move_id','=',move_id), ('journal_id','=',journal_id), ('date','>=',date1), ('date','<=',date2)])
        if not ids:
            return []
        lines_a = self.pool.get('account.analytic.line').browse(self.cr, self.uid, ids) or []
        return lines_a
        
    def _sum_general(self, journal_id, date1, date2,account_ids):
        if account_ids:
            self.cr.execute('SELECT SUM(debit-credit) FROM account_move_line WHERE id IN (SELECT move_id FROM account_analytic_line WHERE (date>=%s) AND (date<=%s) AND (journal_id=%s) AND (move_id is not null)) AND (account_id in %s)', (date1, date2, journal_id,tuple(account_ids)))
        else:
            self.cr.execute('SELECT SUM(debit-credit) FROM account_move_line WHERE id IN (SELECT move_id FROM account_analytic_line WHERE (date>=%s) AND (date<=%s) AND (journal_id=%s) AND (move_id is not null))', (date1, date2, journal_id))
        return self.cr.fetchall()[0][0] or 0

    def _sum_analytic(self, journal_id, date1, date2, account_ids):
        if account_ids:
            self.cr.execute("SELECT SUM(amount) FROM account_analytic_line WHERE date>=%s AND date<=%s AND journal_id=%s AND (account_id in %s)", (date1, date2, journal_id, tuple(account_ids)))
        else:
            self.cr.execute("SELECT SUM(amount) FROM account_analytic_line WHERE date>=%s AND date<=%s AND journal_id=%s", (date1, date2, journal_id))
        res = self.cr.dictfetchone()
        return res['sum'] or 0

report_sxw.report_sxw('report.analytic.account.journal1', 'account.analytic.journal', 'addons/ifrs_account_extension/report/analytic_journal.rml',parser=account_analytic_journal,header="internal")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

