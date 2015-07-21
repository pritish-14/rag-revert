from openerp.osv import osv, fields

class crm_lead(osv.osv):
    _inherit = "crm.lead"

    def _brand_default_get(self, cr, uid, ids, context=None):
        """
        Check if the object for this company have a default value
        """
        if not context:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.brand_id.id

    def _brand_type_get(self, cr, uid, ids, context=None):
        """
        Check if the object for this company have a default value
        """
        if not context:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.brand_id.type

    def lead_meeting_count(self, cr, uid, ids, field_name, arg, context=None):
        Event = self.pool['calendar.event']
        return {
            opp_id: Event.search_count(cr,uid, [('lead_id', '=', opp_id)], context=context)
            for opp_id in ids
        }

    _columns = {
        'channel_id': fields.many2one('crm.tracking.medium', 'Lead Source', help="Communication channel (mail, direct, phone, ...)"),
        'brand_id': fields.many2one('brand', 'Brand', required='True'),
        'manager_id': fields.many2one('res.users', 'Sales Team Manager', select=True, track_visibility='onchange'),        
        'is_lost': fields.boolean('Is Lost'),
        'is_won': fields.boolean('Is Won'),        
        'brand_type': fields.selection([('1', "Radio"), ('2', 'TV'), ('3', 'Digital'), ('4', 'Newspaper')],
		                         "Type"),
        'lead_meeting_count': fields.function(lead_meeting_count, string='# Meetings', type='integer'),		                         
        }

    _defaults = {
        'brand_id': _brand_default_get,
        'brand_type': _brand_type_get,

    }

    def case_mark_won(self, cr, uid, ids, context=None):
        """ Mark the case as won: state=done and probability=100
        """
        stages_leads = {}
        for lead in self.browse(cr, uid, ids, context=context):
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 100.0), ('fold', '=', True)], context=context)
            if stage_id:
                if stages_leads.get(stage_id):
                    stages_leads[stage_id].append(lead.id)
                else:
                    stages_leads[stage_id] = [lead.id]
            else:
                raise osv.except_osv(_('Warning!'),
                    _('To relieve your sales pipe and group all Won opportunities, configure one of your sales stage as follow:\n'
                        'probability = 100 % and select "Change Probability Automatically".\n'
                        'Create a specific stage or edit an existing one by editing columns of your opportunity pipe.'))
        for stage_id, lead_ids in stages_leads.items():
            self.write(cr, uid, lead_ids, {'stage_id': stage_id, 'is_won': True}, context=context)
        return True

    def case_mark_lost(self, cr, uid, ids, context=None):
        """ Mark the case as lost: state=cancel and probability=0
        """
        stages_leads = {}
        for lead in self.browse(cr, uid, ids, context=context):
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 0.0), ('fold', '=', True), ('sequence', '>', 1)], context=context)
            print "stage_id", stage_id
            if stage_id:
                if stages_leads.get(stage_id):
                    stages_leads[stage_id].append(lead.id)
                else:
                    stages_leads[stage_id] = [lead.id]
            else:
                raise osv.except_osv(_('Warning!'),
                    _('To relieve your sales pipe and group all Lost opportunities, configure one of your sales stage as follow:\n'
                        'probability = 0 %, select "Change Probability Automatically".\n'
                        'Create a specific stage or edit an existing one by editing columns of your opportunity pipe.'))
        for stage_id, lead_ids in stages_leads.items():
            self.write(cr, uid, lead_ids, {'stage_id': stage_id, 'is_lost': True}, context=context)
        return True
      
    def create(self, cr, uid, vals, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
	res = super(crm_lead, self).create(cr, uid, vals, context)
        #assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'crm_media', 'email_template_edi_lead')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'crm.lead',
            #'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return res
  
    def on_change_user(self, cr, uid, ids, user_id, context=None):
        """ When changing the user, also set a section_id or restrict section id
            to the ones user_id is member of. """
        section_id = self._get_default_section_id(cr, uid, user_id=user_id, context=context) or False
        if user_id and self.pool['res.users'].has_group(cr, uid, 'base.group_multi_salesteams') and not section_id:
            section_ids = self.pool.get('crm.case.section').search(cr, uid, ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)], context=context)
            if section_ids:
                section_id = section_ids[0]
        return {'value': {'section_id': section_id, 'manager_id': self.pool.get('crm.case.section').browse(cr, uid, section_id).user_id.id}}
        
    def action_schedule_meeting(self, cr, uid, ids, context=None):
        """
        Open meeting's calendar view to schedule meeting on current opportunity.
        :return dict: dictionary value for created Meeting view
        """
        lead = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        partner_ids = [self.pool['res.users'].browse(cr, uid, uid, context=context).partner_id.id]
        if lead.partner_id:
            partner_ids.append(lead.partner_id.id)
        res['context'] = {
            'default_opportunity_id': lead.type == 'opportunity' and lead.id or False,
            'default_partner_id': lead.partner_id and lead.partner_id.id or False,
            'default_partner_ids': partner_ids,
            'default_section_id': lead.section_id and lead.section_id.id or False,
            'default_name': lead.name,
        }
        return res
        
    def action_quotation_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'crm_media', 'email_template_mail')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        ctx.update({
            'default_model': 'crm.lead',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        

class brand(osv.osv):
	_name = 'brand'
	_columns = {
		'name': fields.char("Name", required='True'),
		'type': fields.selection([('1', "Radio"), ('2', 'TV'), ('3', 'Digital'), ('4', 'Newspaper')],
		                         "Type", required='True'),
		'company_id': fields.many2one('res.company', 'Company', required=True, select=1),
		
	}
	
class calendar_event(osv.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'
    _columns = {
    	'status1': fields.selection([
            ('scheduled','Scheduled'),
            ('progress','In Progress'),
            ('complete','Complete'),
            ], 'state'),
     	'status': fields.selection([('scheduled', "Scheduled"), ('progress', 'In Progress'), ('complete', 'Complete')],
		                         "Status", required='True'),
		'lead_id': fields.many2one('crm.lead', 'Lead/Opportunity'),		                         
		        }
		        
    def onchange_status(self, cr, uid, ids, status, context=None):
		if status:
			return {'value' : {'status1': status}}
			
class Users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'brand_id': fields.many2one('brand', 'Brand'),
        'brand_ids':fields.many2many('brand','abc_id','pid','cid','Brands'),
        }

