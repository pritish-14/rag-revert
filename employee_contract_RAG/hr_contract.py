from datetime import datetime, date
import datetime
from openerp.tools.translate import _

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _description = 'Contract'
    _inherit = ['mail.thread', 'hr.contract', 'ir.needaction_mixin']
    _columns = {
        'department_id': fields.related('employee_id','department_id', type='many2one', relation='hr.department', string="Department", readonly=True),
        'staff_no': fields.related('employee_id','department_id', type='integer', string="Staff No", readonly=True),
    	'name': fields.char('Contract Reference'),
        'trial_date_start': fields.date('Probation Period'),
        'visa_expire': fields.date('Visa Expiry Date'),
        'notice_period': fields.float('Notice Period (Days)'),
        'mid_probation_date': fields.date('Mid-Probation Date'),
        'joining_date': fields.date("Joining Date"),
        'status': fields.selection([('on_probation',"On Probation"),
        									  ('confirmed', "Confirmed"),
                                              ('terminated', "Terminated")],
                                             "Status"),
		'status1': fields.selection([('on_probation',"On Probation"),
        									  ('confirmed', "Confirmed"),
                                              ('terminated', "Terminated")],
                                             "Status"),
    }
    
    def onchange_joingdate(self, cr, uid, ids, employee_id, context=None):
        if employee_id:
            date = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            print date
            print date.employment_date
            return {'value' : {'joining_date':date.employment_date }}
    
    def onchange_status(self, cr, uid, ids, status, context=None): 
        if status:
            return {'value' : {'status1':status }}

    def get_date_end(self, cursor, user, context=None):
        date_today = datetime.date.today()
        cursor.execute('select id from hr_contract')
        res=cursor.fetchall()
        print "Resssss", res
        mail_obj = self.pool.get('mail.mail')
        email_template_obj = self.pool.get('email.template')
        for prod_id in res:   
            print prod_id
            rec = self.browse(cursor, user, prod_id[0], context=context)

            print "end date", rec.date_end 
            print date_today.strftime('%Y-%m-%d')
            print datetime.datetime.strptime(rec.date_end, DEFAULT_SERVER_DATE_FORMAT).date()-datetime.timedelta(7)
            a = date_today.strftime('%Y-%m-%d')
            b = str(datetime.datetime.strptime(rec.date_end, DEFAULT_SERVER_DATE_FORMAT).date()-datetime.timedelta(7))
            print "Type A", type(a)
            print "Type B", type(b)
            if a == b:
                ir_model_data = self.pool.get('ir.model.data')
                template_id = self.pool.get('ir.model.data').get_object(cursor, user, 'employee_contract_RAG', 'email_template_edi_contract_expiry_notification_apagen', context=context)
                assert template_id._name == 'email.template'
                print template_id.email_from
                mail_id=email_template_obj.send_mail(cursor, user, template_id.id,
                    rec.id, True, context=context)
                mail_state = mail_obj.read(cursor, user, mail_id, ['state'], 
                    context=context)
                print "Apagen"
                # Checking if the mail is sent properly
                if mail_state and mail_state['state'] == 'exception':
                    raise osv.except_osv(_("Cannot send email. Please check the "\
                    "connection settings and email address properly."),'')
                print "Mail sending"
            else:
                print "Mail not sending"
        return True

    def get_trial_date_end(self, cursor, user, context=None):
        date_today = datetime.date.today()
        cursor.execute('select id from hr_contract')
        res=cursor.fetchall()
        mail_obj = self.pool.get('mail.mail')
        email_template_obj = self.pool.get('email.template')
        print "Resssss", res
        for prod_id1 in res:   
            print prod_id1
            rec = self.browse(cursor, user, prod_id1[0], context=context)

            print "end date", rec.trial_date_end 
            print date_today.strftime('%Y-%m-%d')
            print datetime.datetime.strptime(rec.trial_date_end, DEFAULT_SERVER_DATE_FORMAT).date()-datetime.timedelta(7)
            x = date_today.strftime('%Y-%m-%d')
            y = str(datetime.datetime.strptime(rec.trial_date_end, DEFAULT_SERVER_DATE_FORMAT).date()-datetime.timedelta(7))
            print "Type A", type(x)
            print "Type B", type(y)
            if x == y:
                ir_model_data = self.pool.get('ir.model.data')
                template_id = self.pool.get('ir.model.data').get_object(cursor, user, 'employee_contract_RAG', 'email_template_edi_probation_period_end_notification', context=context)
                assert template_id._name == 'email.template'
                print template_id.email_from
                mail_id=email_template_obj.send_mail(cursor, user, template_id.id,
                    rec.id, True, context=context)
                mail_state = mail_obj.read(cursor, user, mail_id, ['state'], 
                    context=context)
                print "Apagen"
                # Checking if the mail is sent properly
                if mail_state and mail_state['state'] == 'exception':
                    raise osv.except_osv(_("Cannot send email. Please check the "\
                    "connection settings and email address properly."),'')
                print "Mail sending"
            else:
                print "Mail not sending"
        return True

    def get_mid_probation_date(self, cursor, user, context=None):
        date_today = datetime.date.today()
        cursor.execute('select id from hr_contract')
        res=cursor.fetchall()
        mail_obj = self.pool.get('mail.mail')
        email_template_obj = self.pool.get('email.template')

        print "Resssss", res
        for prod_id in res:   
            print prod_id
            rec = self.browse(cursor, user, prod_id[0], context=context)

            print "end date", rec.mid_probation_date 
            print date_today.strftime('%Y-%m-%d')
            print datetime.datetime.strptime(rec.mid_probation_date, DEFAULT_SERVER_DATE_FORMAT)-datetime.timedelta(7)
            a = date_today.strftime('%Y-%m-%d')
            b = str(datetime.datetime.strptime(rec.mid_probation_date, DEFAULT_SERVER_DATE_FORMAT).date()-datetime.timedelta(7))
            if a == b:
                ir_model_data = self.pool.get('ir.model.data')
                template_id = self.pool.get('ir.model.data').get_object(cursor, user, 'employee_contract_RAG', 'email_template_edi_mid_probation_period_end_notification', context=context)
                assert template_id._name == 'email.template'
                print template_id.email_from
                mail_id=email_template_obj.send_mail(cursor, user, template_id.id,
                    rec.id, True, context=context)
                mail_state = mail_obj.read(cursor, user, mail_id, ['state'], 
                    context=context)
                print "Apagen"
                # Checking if the mail is sent properly
                if mail_state and mail_state['state'] == 'exception':
                    raise osv.except_osv(_("Cannot send email. Please check the "\
                    "connection settings and email address properly."),'')

                print "Mail sending"
            else:
                print "Mail not sending"
        return True


