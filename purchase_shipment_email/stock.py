# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import time
import datetime
from openerp.osv import osv, fields

class SendDelayedEmail(osv.osv_memory):
    _inherit = 'stock.picking'

    def send(self, cr, uid, automatic=False, context=None):
        date = datetime.datetime.now().date()

        Picking = self.pool.get('stock.picking')
        picking_ids = Picking.search(cr, uid,
            [('state', 'not in', ['cancel','done']),('min_date','<', str(date))], context=context)

        if not picking_ids:
            return True

        picking_records = Picking.browse(cr, uid, picking_ids, context=context) 
        print picking_records

        if not context:
            context= {}
        email_cc_list = []

        ir_model_data = self.pool.get('ir.model.data')
        Groups = self.pool.get('res.groups') 
        Users = self.pool.get('res.users')
        mail_mail_obj = self.pool.get('mail.mail')

        #CEO'S email ids
        ceo_group_id = ir_model_data.get_object_reference(cr, uid, 'medical_premium', 'group_ceo_apagen')[1]
        ceo_group = Groups.browse(cr, uid, ceo_group_id, context=context)
        for ceos in ceo_group.users:
            for employee in ceos.employee_ids:
                if employee.work_email and employee.work_email not in email_cc_list:
                    email_cc_list.append(employee.work_email)

        #Financial manager email ids
        financial_manager_id = ir_model_data.get_object_reference(cr, uid, 'account', 'group_account_manager')[1]
        financial_groups = Groups.browse(cr, uid, financial_manager_id, context=context)
        for financial in financial_groups.users:
            for employee_financial in financial.employee_ids:
                if employee_financial.work_email and employee_financial.work_email not in email_cc_list:
                    email_cc_list.append(employee_financial.work_email)

        #CTOS mail ids
        cto_id = ir_model_data.get_object_reference(cr, uid, 'purchase_shipment_email', 'group_cto_apagen')[1]
        ctos_groups = Groups.browse(cr, uid, cto_id, context=context)
        for ctos in ctos_groups.users:
            for employee_cto in ctos.employee_ids:
                if employee_cto.work_email and employee_cto.work_email not in email_cc_list:
                    email_cc_list.append(employee_cto.work_email)

        email_template_obj = self.pool.get('email.template')
        template_id = ir_model_data.get_object_reference(cr, uid, 'purchase_shipment_email', 'shipment_delayed_email')[1]
        print "template id >>", str(template_id)
        if template_id:
            for picking_id in picking_ids:
                values = email_template_obj.generate_email(cr, uid, template_id, picking_id, context=context)
                values['email_cc'] = ', '.join(email_cc_list)
                print "valus>>",str(values)     
                msg_id = mail_mail_obj.create(cr, uid, values, context=context)
                print "msg id>>>", str(msg_id)
                if msg_id:
                    mail_mail_obj.send(cr, uid, [msg_id], context=context)
                return True             
             

