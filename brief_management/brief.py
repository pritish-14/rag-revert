from openerp.osv import osv, fields
from datetime import date

class brief(osv.osv):
    _name = "brief"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_default_section_id(self, cr, uid, context=None):
        """ Gives default section by checking if present in the context """
        return self._resolve_section_id_from_context(cr, uid, context=context) or False

    def _resolve_section_id_from_context(self, cr, uid, context=None):
        """ Returns ID of section based on the value of 'section_id'
            context key, or None if it cannot be resolved to a single
            Sales Team.
        """
        if context is None:
            context = {}
        if type(context.get('default_section_id')) in (int, long):
            return context.get('default_section_id')
        if isinstance(context.get('default_section_id'), basestring):
            section_name = context['default_section_id']
            section_ids = self.pool.get('crm.case.section').name_search(cr, uid, name=section_name, context=context)
            if len(section_ids) == 1:
                return int(section_ids[0][0])
        return None

    def get_service(self, cursor, user, context=None):
        product_obj = self.pool.get('ir.model.data').get_object(
            cursor, user, 'brief_management', 'rag_brief_data')
        assert product_obj._name == 'brief.confg'
        return product_obj.survey_id.id

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
        ('pending', 'Pending'),
    ]

    _track = {

        'state': {
            'brief_management.brief_awaiting_approval': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'awaiting_approval',
            'brief_management.brief_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
            'brief_management.brief_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
            'brief_management.brief_pending': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'pending',

        },
    }

    _columns = {
    	'manager_id': fields.many2one('res.users', 'Sales Manager', select=True, track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'advertiser_id': fields.many2one('res.partner', 'Advertiser', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'advertiser_category': fields.many2one('brief.category', 'Category', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'brief_no':fields.char('Brief No.', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'brief_date':fields.date('Brief Date', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'Sales Executive', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'section_id': fields.many2one('crm.case.section', 'Sales Team', help='When sending mails, the default email address is taken from the sales team.', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'brand_id': fields.many2one('brand', 'Brand', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'state': fields.selection(STATE_SELECTION,
            'Status', readonly=True, select=True),
        'notes': fields.text('Notes', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'brief_type': fields.selection([
            ('promotion', 'Promotion'),
            ('classified', 'Classified'),
            ('spot_ads', 'Spot Ads'),
            ], 'Brief Type', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'start_date':fields.date('Expected Start Date', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'end_date':fields.date('Expected End Date', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'due_date': fields.date('Due Date', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'create_by': fields.many2one('res.users','Created By', states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'product': fields.many2one('product.product','Product', readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
#        'job_id': fields.many2one('hr.job', 'Applied Job'),
        'survey_id': fields.many2one('survey.survey', 'Brief Form', help="Choose an Brief form and you will be able to print/answer this briefw from all users ", readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
        'response_id': fields.many2one('survey.user_input', "Response", ondelete='set null', oldname="response", readonly=True, states={'draft':[('readonly',False)],'awaiting_approval':[('readonly',False)]}),
    }
    
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'create_by': lambda obj, cr, uid, context: uid,
        'brief_date': fields.date.context_today,
        'section_id': lambda s, cr, uid, c: s._get_default_section_id(cr, uid, c),
        'state': 'draft',
        'survey_id': get_service,
    }

    def action_start_survey(self, cr, uid, ids, context=None):
        context = dict(context or {})
        applicant = self.browse(cr, uid, ids, context=context)[0]
        survey_obj = self.pool.get('survey.survey')
        response_obj = self.pool.get('survey.user_input')
        # create a response and link it to this applicant
        if not applicant.response_id:
            response_id = response_obj.create(cr, uid, {'survey_id': applicant.survey_id.id, 'partner_id': applicant.partner_id.id}, context=context)
            self.write(cr, uid, ids[0], {'response_id': response_id}, context=context)
        else:
            response_id = applicant.response_id.id
        # grab the token of the response and start surveying
        response = response_obj.browse(cr, uid, response_id, context=context)
        context.update({'survey_token': response.token})
        return survey_obj.action_start_survey(cr, uid, [applicant.survey_id.id], context=context)

    def action_print_survey(self, cr, uid, ids, context=None):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        context = dict(context or {})
        applicant = self.browse(cr, uid, ids, context=context)[0]
        survey_obj = self.pool.get('survey.survey')
        response_obj = self.pool.get('survey.user_input')
        if not applicant.response_id:
            return survey_obj.action_print_survey(cr, uid, [applicant.survey_id.id], context=context)
        else:
            response = response_obj.browse(cr, uid, applicant.response_id.id, context=context)
            context.update({'survey_token': response.token})
            return survey_obj.action_print_survey(cr, uid, [applicant.survey_id.id], context=context)
    
    def on_change_user(self, cr, uid, ids, user_id, context=None):
        """ When changing the user, also set a section_id or restrict section id
            to the ones user_id is member of. """
#        section_id = self._get_default_section_id(cr, uid, user_id=user_id, context=context) or False
        if user_id and self.pool['res.users'].has_group(cr, uid, 'base.group_multi_salesteams'):
            section_ids = self.pool.get('crm.case.section').search(cr, uid, ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)], context=context)
            if section_ids:
                section_id = section_ids[0]
                manager_id = self.pool.get('crm.case.section').browse(cr, uid, section_id).user_id                            
                return {'value': {'section_id': section_id, 'manager_id': manager_id.id}}

    def on_change_customer(self, cr, uid, ids, partner_id, context=None):
		if partner_id:
			return {'value' : {'advertiser_id': partner_id}}	
	

    def submit_request(self, cr, uid, ids, context=None):
        seq = self.pool.get('ir.sequence').get(cr, uid, 'brief') or '/'
        self.write(cr, uid, ids, {'state': 'awaiting_approval', 'brief_no': seq})
        return True

    def approve_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved'})
        return True

    def cancel_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def pending_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'pending'})
        return True

    def reset_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True    

class brand(osv.osv):
    _name = 'brand'
    _columns = {
        'name': fields.char("Name", required='True'),
        'type': fields.selection([('1', "Radio"), ('2', 'TV'), ('3', 'Digital')],
                                 "Type", required='True'),
        'company_id': fields.many2one('res.company', 'Company', required=True, select=1),
        
    }        

class brief_category(osv.osv):
    _name = 'brief.category'
    _columns = {
        'name': fields.char("Name")
        }
        
class brief_category(osv.osv):
    _name = 'brief.confg'
    _columns = {
        'name': fields.char('Name'),
        'survey_id': fields.many2one('survey.survey', 'Brief Form', help="Choose an Brief form and you will be able to print/answer this briefw from all users "),

        }
        
