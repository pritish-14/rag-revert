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
from openerp.osv import fields, osv

class account_analytic_journal_report(osv.osv_memory):
    _inherit = 'account.analytic.journal.report'

    _columns = {
        'account_ids': fields.many2many('account.account', 'account_analytic_journal_report_rel_ifrs', 'account_id', 'id6', 'Accounts'),
    }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        ids_list = []
        record = self.browse(cr,uid,ids[0],context=context)
        if context.get('active_id',False):
            ids_list.append(context.get('active_id',False))
        else:
            for analytic_record in record.analytic_account_journal_id:
                ids_list.append(analytic_record.id)
        acc_ids = record.account_ids
        accounts = [acc.id for acc in acc_ids]  
        print "data:::::::::+_+_+_",data
        datas = {
             'ids': ids_list,
             'model': 'account.analytic.journal',
             'form': data
                 }
        datas['form'].update({'account_ids' : accounts})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'analytic.account.journal1',
            'datas': datas,
            }
        
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(account_analytic_journal_report, self).default_get(cr, uid, fields, context=context)
        if not context.has_key('active_ids'):
            journal_ids = self.pool.get('account.analytic.journal').search(cr, uid, [], context=context)
        else:
            journal_ids = context.get('active_ids')
        if 'analytic_account_journal_id' in fields:
            res.update({'analytic_account_journal_id': journal_ids})
        return res
    
account_analytic_journal_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
