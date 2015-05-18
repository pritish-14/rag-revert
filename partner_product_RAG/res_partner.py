from openerp.osv import fields,osv
from datetime import date

class res_partner(osv.osv):
    """ Inherits partner and adds CRM information in the partner form """
    _inherit = 'res.partner'

    _columns = {
        'dob':fields.date('Date of Birth'),    
        'pin': fields.char('PIN', size=32),
        'vat_no': fields.char('VAT No.', size=32),
        'code': fields.char('Code', size=32),
        'giro_no': fields.integer('GIRO No.'),
        'is_advertiser': fields.boolean('Advertiser'),
        'is_agency': fields.boolean('Agency'),
        'industry_id': fields.many2one('partner.industry', 'Industry')
    }

class partner_industry(osv.osv):
    _name = 'partner.industry'

    _columns = {
        'name': fields.char('Name', size=32),
    }

'''def send_birthday_email(self, cr, uid, ids=None, context=None):
        partner_obj = self.pool.get('res.partner')
        mail_mail = self.pool.get('mail.mail')
        mail_ids = []
        today = datetime.datetime.now()    
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')    
        par_id = partner_obj.search(cr, uid, [ ('customer','=',True),('dob','like',today_month_day)])
        if par_id:
            try:
                for val in partner_obj.browse(cr, uid, par_id):
                    email_from = val.email
                    name = val.name                
                    subject = "Birthday Wishes"
                    body = _("Hello %s,\n" %(name))                 
                    body += _("\tWish you Happy Birthday\n")                     
                    footer = _("Kind regards.\n")         
                    footer += _("%s\n\n"%val.company_id.name)
                    mail_ids.append(mail_mail.create(cr, uid, {
                        'email_to': email_from,
                        'subject': subject,
                        'body_html': '<pre><span class="inner-pre" style="font-size: 15px">%s<br>%s</span></pre>' %(body, footer)
                     }, context=context))
                    mail_mail.send(cr, uid, mail_ids, context=context)            
            except Exception, e:
                print "Exception", e    
        return None'''

