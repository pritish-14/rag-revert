import time
import datetime

from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_picking(osv.Model):
    _inherit = "stock.picking"
    _columns = {
        'issue_order_id': fields.many2one('issue.order', 'Issue Order', readonly=True),
    }
'''
class stock_picking_in(osv.Model):
    _inherit = "stock.picking"
    _columns = {
        'issue_order_id': fields.many2one('issue.order', 'Issue Order', readonly=True),
    }
'''

class material_request(osv.Model):
    '''
    Material Request
    '''

    _name = 'material.request'
    _inherit = ['mail.thread']
    _description = 'Material Request'

    def _current_employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False

    _columns = {
        'test': fields.char('Set',size=64),
        'employee_id': fields.many2one('res.users', 'Requested By', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'department_id': fields.many2one('hr.department', 'Department', readonly=True, states={'draft':[('readonly',False)]}),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'analytic_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True, states={'draft':[('readonly',False)]}),
        'project_id': fields.many2one('project.project', 'Project'),
        'name': fields.char('Material Request'),
        'warehouse_id': fields.many2one('stock.warehouse', 'Destination Warehouse',  readonly=True, states={'draft':[('readonly',False)]}),
        'request_date': fields.datetime('Request Date'),
        'required_date': fields.date('Required Date', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'material_ids': fields.one2many('stock.material', 'request_id', 'Materials', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft','Draft'),
            #('waiting', 'Awaiting Warehouse Acceptance'),
           # ('waiting_pmo_approval', 'Awaiting PMO Approval'),
            ('waiting_hod_approval', 'Awaiting Approval'),
            ('accept','Approved'),
           #('refuse','Refused'),
            ('cancel','Cancelled'),
            ],'Status', select=True, readonly=True, track_visibility='onchange'),
        'subcontractor_check': fields.boolean('Sub-Contractor', readonly=True, states={'draft':[('readonly',False)]}, help='Check this box if it is subcontractor.'),
        'subcontractor_id':fields.many2one('res.partner', 'Sub-Contractor', readonly=True, states={'draft':[('readonly',False)]}),
        'subcontractor_address_id': fields.many2one('res.partner', 'Sub-Contractor Contact', readonly=True, help="Sub Contractor address", states={'draft':[('readonly',False)]}),
        'dest_location_id': fields.many2one('stock.location', 'Destination Location', readonly=True, states={'draft':[('readonly',False)]}),
        'user_id' : fields.many2one('res.users', 'Users'),
    }

    _defaults = {
        'state': 'draft',
        'employee_id': lambda obj, cr, uid, context: uid,
#        'name': lambda obj, cr, uid, context: '/',
        #'request_date': fields.date.context_today, #to be able to have date in user's timezone
        'subcontractor_address_id': lambda self, cr, uid, context: context.get('subcontractor_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['default'])['default'],
        'user_id' : lambda self, cr, uid, context=None: uid,
    }
    
    def onchange_subcontractor_id(self, cr, uid, ids, subcontractor_id, context=None):
        if not subcontractor_id:
            return {'value': {'dest_location_id': False}}
        dest_location_id = self.pool.get('res.partner').browse(cr, uid, subcontractor_id).property_stock_supplier.id
        return {'value' : {'dest_location_id': dest_location_id or False}}

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        if not warehouse_id:
            return {'value': {'dest_location_id': False}}
        dest_location_id = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id).lot_stock_id.id
        return {'value': {'dest_location_id': dest_location_id or False}}

    def onchange_account(self, cr, uid, ids, analytic_id, context=None):
        if not analytic_id:
            return {'value': {'project_id': False}}
        project_obj = self.pool.get('project.project')
        project_ids = project_obj.search(cr, uid, [('analytic_account_id', '=', analytic_id)])
        return {'value': {'project_id': project_ids and project_ids[0] or False}}

    def onchange_subcontractor_address_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'subcontractor_address_id': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        dest_location_id = part.property_stock_supplier.id
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['default','delivery', 'invoice', 'contact'])
        val = {
            'subcontractor_address_id': addr['default'],
            'dest_location_id' : dest_location_id
        }

        return {'value': val}
    
    def write(self, cr, uid, ids, vals, context=None):
        res_user_obj = self.pool.get('res.users')
        res_partner_obj = self.pool.get('res.partner')
        part_ids = []
        name = ''
        emp_name = ''
        material_req_data = self.browse(cr, uid, ids[0], context=context)
        if material_req_data:
            
            if material_req_data.employee_id:
                emp_name = material_req_data.employee_id.name 
                #+ ' ' + material_req_data.employee_id.surname
                emp_ids = res_partner_obj.search(cr, uid, [('name','=',emp_name)], context=context)
                if emp_ids:
                    part_ids.append(emp_ids[0])
            if material_req_data.department_id:
                if material_req_data.department_id.manager_id:
                    name = material_req_data.department_id.manager_id.name + ' ' + material_req_data.department_id.manager_id.surname
                    partner_ids = res_partner_obj.search(cr, uid, [('name','=',name)], context=context)
                    if partner_ids:
                        part_ids.append(partner_ids[0])
        user_ids1 = res_partner_obj.search(cr, uid, [('name','=','Anderson Naagbi')], context=context)
        user_ids2 = res_partner_obj.search(cr, uid, [('name','=','Kester Onianwa')], context=context)
        if user_ids1:
            part_ids.append(user_ids1[0])
        if user_ids2:
            part_ids.append(user_ids2[0])
        if part_ids:
            vals.update({'message_follower_ids' : [(6,0,part_ids)]})
    
        return super(material_request, self).write(cr, uid, ids, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['name'] = '/'
        return super(material_request, self).copy(cr, uid, id, default, context)

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, 1, 'material.request') or '/'
        return super(material_request, self).create(cr, uid, vals, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'waiting_hod_approval', 'request_date': datetime.datetime.today()}, context=context)
    
    def action_pmo_approval(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.write(cr, uid, ids, {'state': 'waiting_hod_approval'}, context=context)
    
    def action_hod_approval(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        compose_obj = self.pool.get('mail.compose.message')
        data = self.browse(cr, uid, ids[0], context=context)
        if data:
            template_ids = self.pool.get('email.template').search(cr, uid, [('model_id.model', '=', 'material.request')])
            if template_ids:
                compose_vals = compose_obj.generate_email_for_composer(cr, uid, template_ids[0], data.id, context=context)
                partner_ids = self.pool.get('res.partner').search(cr, uid, [('name', '=', 'Warehouse Department')])
                #compose_vals['partner_ids'] = [(6, 0, partner_ids)]
                compose_vals.update(partner_ids=[(6, 0, partner_ids)])
                compose_id = compose_obj.create(cr, uid, compose_vals,
                {'default_composition_mode': 'comment', 'default_model': 'material.request', 'default_res_id': data.id})
                compose_obj.send_mail(cr, uid, [compose_id])
        return self.write(cr, uid, ids, {'state': 'waiting'}, context=context)

    def action_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def action_accept(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        loc_obj = self.pool.get('stock.location')
        warehouse_obj = self.pool.get('stock.warehouse')
        issue_order_obj = self.pool.get('issue.order')
        project_obj = self.pool.get('project.project')
        ir_model_data = self.pool.get('ir.model.data')
        compose_obj = self.pool.get('mail.compose.message')
        self.write(cr, uid, ids, {'state': 'accept'}, context=context)
        order_requence = self.pool.get('ir.sequence').get(cr, uid, 'issue.order') or '/'
        user_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        warehouse_ids = warehouse_obj.search(cr, uid, [('company_id', '=', user_company_id)], context=context)
        
        loc_id = False
        if warehouse_ids:
            loc_id = warehouse_obj.browse(cr, uid, warehouse_ids[0], context=context).lot_stock_id.id
        for request in self.browse(cr, uid, ids, context=context):
            
            material_ids = [material.id for material in request.material_ids]
            project_id = False
            project_ids = project_obj.search(cr, uid, [('analytic_account_id', '=', request.analytic_id.id)])
            if project_ids:
                project_id = project_ids[0]
            
            
            order_id = issue_order_obj.create(cr, uid,{'name': order_requence,
                            'material_req_id' : request.id,
                            'origin': request.name,
                            'employee_id':request.employee_id.id,
                            'department_id':request.department_id.id,
                            'company_id': request.company_id.id,
                            'delivery_date': request.required_date,
                            'location_id': loc_id,
                            'dest_location_id':request.dest_location_id and request.dest_location_id.id or False,
                            'material_ids': [(4, id) for id in material_ids],
                            'analytic_id': request.analytic_id.id or False,
                            'project_id': project_id,
                            'subcontractor_id': request.subcontractor_id and request.subcontractor_id.id or False,
                            'subcontractor_address_id': request.subcontractor_id and request.subcontractor_address_id.id or False
                        })
        return True
#        form_res = ir_model_data.get_object_reference(cr, uid, 'material_issue_register', 'view_issue_order_form')
#        form_id = form_res and form_res[1] or False
#        return {
#            'name': _('Issue Order'),
#            'view_type': 'form',
#            'view_mode': 'form',
#            'res_model': 'issue.order',
#            'res_id': order_id,
#            'view_id': form_id,
#            'context': context,
#            'type': 'ir.actions.act_window',
#        }

    def action_refuse(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'refuse'}, context=context)
        return True

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        if not employee_id: return {'value': {'department_id': False, 'company_id': False}}
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        department_id = False
        company_id = False
        if employee.department_id:
            department_id = employee.department_id.id
        if employee.company_id:
            company_id = employee.company_id.id
        return {'value': {'department_id': department_id, 'company_id': company_id}}


class stock_material(osv.Model):
    _name = 'stock.material'
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one('product.product', 'Material', required=True),
        'qty': fields.float('Quantity', required=True),
        'uom_id': fields.many2one('product.uom', 'Unit Of Measure', required=True),
        'lot_id': fields.many2one('stock.production.lot', 'Serial Number'),
        'request_id': fields.many2one('material.request', 'Material Request'),
        'issue_id': fields.many2one('issue.order', 'Issue Order'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {'value': {}}
        prod_obj = self.pool.get('product.product')
        product = prod_obj.browse(cr, uid, product_id)
        return {'value': {'uom_id': product.uom_id.id, 'qty': 1.0}}

class issue_order(osv.osv):
    '''
    Issue Order
    '''

    _name = 'issue.order'
    _inherit = ['mail.thread']
    _description = 'Issue Order'

    def _current_employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False
    
    def _group_readonly(self, cr, uid, ids, name, args, context=None):
        res = {}
        justread = True
        data = self.browse(cr, uid, ids[0], context=context)
        
        warehouse_user_group = self.pool.get('ir.model.data').get_object(cr, uid, 'stock', 'group_stock_user')
        warehouse_users = [user.id for user in warehouse_user_group.users]

        warehouse_manager_group = self.pool.get('ir.model.data').get_object(cr, uid, 'stock', 'group_stock_manager')
        warehouse_manager_users = [user.id for user in warehouse_manager_group.users]

        if uid in warehouse_users and data.state in ('draft', 'waiting'):
            justread = False
        elif uid in warehouse_manager_users and data.state in ('draft', 'waiting'):
            justread = False
        
        res[ids[0]] = justread
        return res
    
    def _get_readonly(self, cr, uid, context=None):
        res = True
        return res

    _columns = {
        'employee_id': fields.many2one('res.users', 'Requested By', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'department_id': fields.many2one('hr.department', 'Department', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'analytic_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True),
        'project_id': fields.many2one('project.project', 'Project'),
        'name': fields.char('Issue Order', readonly=True),
        'origin': fields.char('Material Request Ref', readonly=True),
        'location_id': fields.many2one('stock.location', 'Source Location', required=True, states={'draft': [('readonly', False)]}),
        'dest_location_id': fields.many2one('stock.location', 'Destination Location'),
        'issuer_id': fields.many2one('res.users', 'Issued By', states={'draft': [('readonly', False)], 'waiting': [('readonly', False), ('required', True)]}),
        'issue_date': fields.datetime('Issue Date', readonly='1'),
        'delivery_date': fields.date('Delivery Date', readonly=True),
        'material_ids': fields.one2many('stock.material', 'issue_id', 'Materials'),
        'lpo': fields.char('LPO No.', readonly=True, states={'draft': [('readonly', False)]}),
        'vehicle': fields.char('Vehicle No.', readonly=True, states={'draft': [('readonly', False)]}),
        'driver': fields.char('Driver Name', readonly=True, states={'draft': [('readonly', False)]}),
        'origin': fields.char("Source Document"),
        'state': fields.selection([
            ('draft','Draft'),
            ('waiting','Awaiting Approval'),
            ('issue','Issued'),
            #('refuse','Refused'),
            ('cancel','Cancelled'),
            ],'Status', select=True, readonly=True,track_visibility='onchange'),
        'subcontractor_check': fields.boolean('Sub-Contractor', readonly=True, states={'draft':[('readonly',False)]}, help='Check this box if it is subcontractor.'),
        'subcontractor_id':fields.many2one('res.partner', 'Sub-Contractor', readonly=True),
        'subcontractor_address_id': fields.many2one('res.partner', 'Sub-Contractor Contact', readonly=True, help="Sub Contractor address "),
        'request_date': fields.datetime('Request Date', readonly='1'),
        'group_readonly': fields.function(_group_readonly, string='Group Readonly', type='boolean'),
        'material_req_id' : fields.many2one('material.request', 'Material Request', readonly=True)
    }

    _defaults = {
        'state': 'draft',
        'employee_id': lambda obj, cr, uid, context: uid,
        'group_readonly': _get_readonly,
        #'request_date': fields.date.context_today, #to be able to have date in user's timezone
    }

    def onchange_account(self, cr, uid, ids, analytic_id, context=None):
        if not analytic_id:
            return {'value': {'project_id': False}}
        project_obj = self.pool.get('project.project')
        project_ids = project_obj.search(cr, uid, [('analytic_account_id', '=', analytic_id)])
        return {'value': {'project_id': project_ids and project_ids[0] or False}}

    def onchange_subcontractor_address_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'subcontractor_address_id': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['default','delivery', 'invoice', 'contact'])
        val = {
            'subcontractor_address_id': addr['default'],
        }

        return {'value': val}


    def action_confirm1(self, cr, uid, ids, context=None):
        compose_obj = self.pool.get('mail.compose.message')
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            if not order.material_ids:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a request which has no line.'))
            template_ids = self.pool.get('email.template').search(cr, uid, [('model_id.model', '=', 'issue.order')])
            if template_ids:
                compose_vals = compose_obj.generate_email_for_composer(cr, uid, template_ids[0], order.id, context=context)
                partner_ids = self.pool.get('res.partner').search(cr, uid, [('name', '=', 'Warehouse Department')])
                compose_vals['partner_ids'] = [(6, 0, partner_ids)]
                compose_id = compose_obj.create(cr, uid, compose_vals,
                {'default_composition_mode': 'comment', 'default_model': 'issue.order', 'default_res_id': order.id})
                compose_obj.send_mail(cr, uid, [compose_id])
        self.write(cr, uid, ids, {'state': 'waiting', 'request_date': datetime.datetime.today()}, context=context)
        return True

    def action_draft(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def action_issue(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_obj = self.pool.get('stock.picking')
        seq = self.pool.get('ir.sequence').get(cr, uid, 'issue.order') or '/'
        move_obj = self.pool.get('stock.move')
        self.write(cr, uid, ids, {'state': 'issue', 'name': seq, 'issue_date': time.strftime('%Y-%m-%d')}, context=context)
        '''move_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            for material in order.material_ids:
                print "00000000000000000000000000000000000000000000000000", material.uom_id.id, material.qty, material.product_id.name,order.request_date,order.location_id.id, order.dest_location_id.id,order.issuer_id.id,order.analytic_id.id
                move_ids.append(move_obj.create(cr, uid, {
                            'product_id': material.product_id.id,
                            'product_uom': material.uom_id.id,
                            'product_uom_qty': material.qty,
                            'name': material.product_id.name,
                            'date_expected': order.request_date,
                            'location_id': order.location_id.id,
                            'location_dest_id': order.dest_location_id.id,
                            'receiver_id': order.issuer_id.id,
                            'analytic_id': order.analytic_id.id or False,
                            }))
            project_id = self.pool.get('project.project').search(cr, uid, [('analytic_account_id', '=', order.analytic_id.id)])
            picking_id = picking_obj.create(cr, uid, {
                        'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                        'origin': order.name or '',
                        'issue_order_id': order.id,
                     #   'min_date': datetime.datetime.strptime(order.delivery_date+" 00:00:00", '%Y-%m-%d %H:%M:%S'),
                        'date': order.issue_date or False,
                        'move_lines': [(4, id) for id in move_ids],
                        'type': 'in',
                        'analytic_id': order.analytic_id.id or False,
                        'project_id': project_id and project_id[0] or False,
                        'state': 'draft',
                        'subcontractor_check':order.subcontractor_check,
                        'subcontractor_id': order.subcontractor_id.id,
                        'subcontractor_address_id': order.subcontractor_address_id.id,
                        })'''
        return True

    def action_refuse(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'refuse'}, context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        if not employee_id: return {'value': {'department_id': False, 'company_id': False}}
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        department_id = False
        company_id = False
        if employee.department_id:
            department_id = employee.department_id.id
        if employee.company_id:
            company_id = employee.company_id.id
        return {'value': {'department_id': department_id, 'company_id': company_id}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
