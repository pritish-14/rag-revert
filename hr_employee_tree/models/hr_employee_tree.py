from openerp.osv import osv,fields

class hr_employee(osv.Model):   
    _name = 'hr.employee' 
    _inherit = ['hr.employee']
    
    def do_follow(self, cr, uid, ids, user_ids=None, subtype_ids=None, context=None):
        return self.message_subscribe_users(cr, uid, ids, user_ids=user_ids, subtype_ids=None, context=context)

    def do_unfollow(self, cr, uid, ids, user_ids=None, context=None):
        """ Wrapper on message_subscribe, using users. If user_ids is not
            provided, unsubscribe uid instead. """
        return self.message_unsubscribe_users(cr, uid, ids, user_ids=user_ids, context=context)

    _columns = {
    }
    #recent data :
    def get_recent_activities(self, cr, uid, emp_id, context=None):
        employee_browse = self.browse(cr, uid, emp_id, context=context)
        result = {}
        if not employee_browse.user_id:
            return {}
        partner_id = employee_browse.user_id.partner_id.id
        message_obj = self.pool['mail.message']
        message_ids = message_obj.search(cr,uid,[('model', '=', 'res.partner'),('res_id', '=', partner_id)],context=context)
        if message_ids:
            
            result =  message_obj.read(cr, uid, message_ids, ['id','author_avatar','date','subject'], context=context)
            result[0]['author_avatar'] = 'data:image/*;base64,'+ result[0]['author_avatar']
            return result
        return result
    #get employee data for chart
    def get_employee(self, cr, uid, ids=None, domain=None, context=None, limit=None):
        domain = domain if domain is not None else []
        limit = limit if limit is not None else 100
        employee_ids = self.search(cr, uid, domain, context=context, limit=limit)
        result = self.read(cr, uid, employee_ids, ['id', 'parent_id', 'name', 'image', 'job_id', 'department_id', 'message_is_follower' ], context)
        company_data = {}
        res_users = self.pool['res.users']
        comp_ids = res_users.read(cr,uid,uid,[],context=context)
        company_data = {'name':comp_ids['name'], 'parent_id':'False', 'dept':'','post':'', 'id':'companyid_'+str(comp_ids['id']),'model':'res.company', 'image':'data:image/*;base64,'+comp_ids['image']}
        return [result,company_data]
