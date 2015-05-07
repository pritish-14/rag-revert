from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from openerp import SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime
from psycopg2 import OperationalError
import openerp

class procurement_order(osv.osv):
    _inherit = "procurement.order"
    
    def _procure_orderpoint_confirm(self, cr, uid, use_new_cursor=False, company_id = False, context=None):
        '''
        Create procurement based on Orderpoint

        :param bool use_new_cursor: if set, use a dedicated cursor and auto-commit after processing each procurement.
            This is appropriate for batch jobs only.
        '''
        if context is None:
            context = {}
        if use_new_cursor:
            cr = openerp.registry(cr.dbname).cursor()
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')

        procurement_obj = self.pool.get('procurement.order')
        dom = company_id and [('company_id', '=', company_id)] or []
        orderpoint_ids = orderpoint_obj.search(cr, uid, dom)
        prev_ids = []
        while orderpoint_ids:
            ids = orderpoint_ids[:100]
            del orderpoint_ids[:100]
            for op in orderpoint_obj.browse(cr, uid, ids, context=context):
                try:
                    prods = self._product_virtual_get(cr, uid, op)
                    if prods is None:
                        continue
                    if float_compare(prods, op.product_min_qty, precision_rounding=op.product_uom.rounding) < 0:
                        qty = max(op.product_min_qty, op.product_max_qty) - prods
                        reste = op.qty_multiple > 0 and qty % op.qty_multiple or 0.0
                        if float_compare(reste, 0.0, precision_rounding=op.product_uom.rounding) > 0:
                            qty += op.qty_multiple - reste

                        if float_compare(qty, 0.0, precision_rounding=op.product_uom.rounding) <= 0:
                            continue

                        qty -= orderpoint_obj.subtract_procurements(cr, uid, op, context=context)

                        qty_rounded = float_round(qty, precision_rounding=op.product_uom.rounding)
                        if qty_rounded > 0:
                            assert len(ids) == 1, 'This option should only be used for a single id at a time.'
                            ir_model_data = self.pool.get('ir.model.data')
                            try:
                                template_id = ir_model_data.get_object_reference(cr, uid, 'sale', 'sale.email_template_edi_sale')[1]
                            except ValueError:
                                template_id = False
                            try:
                                compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
                            except ValueError:
                                compose_form_id = False 
                            ctx = dict()
                            ctx.update({
                                'default_model': 'procurement.order',
                                'default_res_id': ids[0],
                                'default_use_template': bool(template_id),
                                'default_template_id': template_id,
                                'default_composition_mode': 'comment',
                                'mark_so_as_sent': True
                            })
                        
                            proc_id = procurement_obj.create(cr, uid,
                                                             self._prepare_orderpoint_procurement(cr, uid, op, qty_rounded, context=context),
                                                             context=context)
                            self.check(cr, uid, [proc_id])
                            self.run(cr, uid, [proc_id])
                    if use_new_cursor:
                        cr.commit()
                except OperationalError:
                    if use_new_cursor:
                        orderpoint_ids.append(op.id)
                        cr.rollback()
                        continue
                    else:
                        raise
            if use_new_cursor:
                cr.commit()
            if prev_ids == ids:
                break
            else:
                prev_ids = ids

        if use_new_cursor:
            cr.commit()
            cr.close()
        return {}    
