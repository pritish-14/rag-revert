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

from openerp.osv import fields, osv

class account_changes_in_equity(osv.osv_memory):
    _inherit = "account.common.account.report"
    _name = 'account.changes.in.equity'
    _description = 'Changes in equity'

    _defaults = {
        'journal_ids': [],
        'display_account': 'all',
        'target_move': 'all',
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml', 'report_name': 'change.in.equity', 'datas': data}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
