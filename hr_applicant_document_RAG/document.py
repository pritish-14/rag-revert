from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
from datetime import datetime,date
from json import dumps
import time
import datetime

class ir_attachment(osv.osv):
	_inherit = 'ir.attachment'
	_description = 'Document Resume Letters'
	
	def _name_get_resname(self, cr, uid, ids, object, method, context):
		data = {}
		for attachment in self.browse(cr, uid, ids, context=context):
			model_object = attachment.res_model
			res_id = attachment.res_id
			if model_object and res_id:
				model_pool = self.pool[model_object]
				res = model_pool.name_get(cr,uid,[res_id],context)
				res_name = res and res[0][1] or None
				if res_name:
					field = self._columns.get('res_name',False)
					if field and len(res_name) > field.size:
						res_name = res_name[:30] + '...'
					data[attachment.id] = res_name or False
				else:
					data[attachment.id] = False
			return data
			
	def _get_default_value(self, cr, uid, context=None):
		res = self.pool.get('document.directory').search(cr, uid, [('name','=','Resumes and Letters')], context=context)
		return res and res[0] or False
	
	_columns = {
		'res_name': fields.function(_name_get_resname, type='char', string='Resource Name', store=True),
        'res_model': fields.char('Resource Model', readonly=True, help="The database object this attachment will be attached to"),
        'res_id': fields.integer('Resource ID', readonly=True, help="The record id this is attached to"),
        'parent_id': fields.many2one('document.directory', 'Directory', select=1, change_default=True, readonly= True),
    }

 	_defaults = {
 		'parent_id': _get_default_value,
	}
    
	
