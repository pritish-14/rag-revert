import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv

class asset_category(osv.osv):
    _inherit = 'account.asset.category'
    _description = 'Asset category'

    _columns = {
        'useful_life_years': fields.integer('Useful Life (Years)'),
        'method': fields.selection([('linear','Linear'),('degressive','Degressive'),('straight_line','Straight Line')], 'Computation Method', required=True),
    }

    _defaults = {
        'useful_life_years': 0,
        'method': 'straight_line',
    }


class account_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _description = 'Asset'

    def _dep_period(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        val = 0.0
        for record in self.browse(cr, uid, ids, context=context):
            if record.depreciation_line_ids:        
                for acc in record.depreciation_line_ids: 
                    if acc.depreciation_date <= datetime.now().strftime('%Y-%m-%d %H:%M:%S'):                       
                        value = acc.depreciated_value
                        result[record.id] = value                                        
        return result
        
    def _current_value(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        val = 0.0
        for record in self.browse(cr, uid, ids, context=context):
            if record.depreciation_line_ids:        
                value = record.purchase_value - record.total_depreciation
                result[record.id] = value                                        
        return result

    def _total_depreciation(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        val = 0.0
        print "<<<<<<<<", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for record in self.browse(cr, uid, ids, context=context):
            if record.depreciation_line_ids:
                for acc in record.depreciation_line_ids:
                    print acc.depreciation_date
                    if acc.depreciation_date <= datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                        val = acc.amount
                    result[record.id] = val                            
        return result

    _columns = {
    
    	'state': fields.selection([('draft','Draft'),('open','Running'),('close','Close')], 'Status', required=True, copy=False,
                                  help="When an asset is created, the status is 'Draft'.\n" \
                                       "If the asset is confirmed, the status goes in 'Running' and the depreciation lines can be posted in the accounting.\n" \
                                       "You can manually close an asset when the depreciation is over. If the last line of depreciation is posted, the asset automatically goes in that status."),
    	'asset_no':fields.char("Asset"),
        'dep_period': fields.function(_dep_period, type="float", string='Depreciation Period'),        
        'current_value': fields.function(_current_value, type="float", string='Current Value'),    
        'total_depreciation': fields.function(_total_depreciation, type="float", string='Total Depreciation'),    
        'location_id': fields.char('Location',readonly=True, states={'draft':[('readonly',False)]}),
        #'location_id': fields.many2one('stock.location', 'Location'),
        'method': fields.selection([('linear','Linear'),('degressive','Degressive'),('straight_line','Straight Line')], 'Computation Method', required=True, readonly=True, states={'draft':[('readonly',True)]}),
        'depreciation_frequency': fields.selection([('yearly','Yearly'),('monthly','Monthly')], 'Depreciation Frequency', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'method_number': fields.integer('Number of Depreciations', readonly=True, states={'draft':[('readonly',False)]}, help="The number of depreciations needed to depreciate your asset"),
        'method_period': fields.integer('Number of Months in a Period', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The amount of time between two depreciations, in months"),
        
        #'method_period': fields.integer('Number of Months in a Period'),
        #'method_end': fields.date('Ending Date', readonly=True, states={'draft':[('readonly',False)]}),
        'method_time': fields.selection([('number','Number of Depreciations'),('end','Ending Date')], 'Time Method', required=False, readonly=True, states={'draft':[('readonly',True)]},
                                  help="Choose the method to use to compute the dates and number of depreciation lines.\n"\
                                       "  * Number of Depreciations: Fix the number of depreciation lines and the time between 2 depreciations.\n" \
                                       "  * Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond."),
        'prorata':fields.boolean('Prorata Temporis', readonly=True, states={'draft':[('readonly',False)]}, help='Indicates that the first depreciation entry for this asset have to be done from the purchase date instead of the first January'),
        'brand_id': fields.many2one('brand', "Brand", readonly=True, states={'draft':[('readonly',False)]}),
    }

    _defaults = {
        #'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'account.asset.asset',context=context),
        'method': 'straight_line',
        'depreciation_frequency': 'monthly'
    }
    
    '''def create(self, cr, uid, vals, context=None):
        if vals.get('asset_no','/')=='/':
            vals['asset_no'] = self.pool.get('ir.sequence').get(cr, uid, 'account.asset.asset') or '/'
        return super(account_asset, self).create(cr, uid, vals, context=context)'''
    
    def validate(self, cr, uid, ids, vals, context=None):
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        if vals.get('asset_no','/')=='/':
            vals['asset_no'] = self.pool.get('ir.sequence').get(cr, uid, 'account.asset.asset') or '/'
        return self.write(cr, uid, ids, vals, context)

    def set_to_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    def _compute_board_amount(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None):
        #by default amount = 0
        amount = 0
        if i == undone_dotation_number:
            amount = residual_amount
        else:
            if asset.method == 'straight_line':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if asset.prorata:
                    amount = amount_to_depr / asset.method_number
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (amount_to_depr / asset.method_number) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (amount_to_depr / asset.method_number) / total_days * (total_days - days)
            elif asset.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if asset.prorata:
                    amount = amount_to_depr / asset.method_number
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (amount_to_depr / asset.method_number) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (amount_to_depr / asset.method_number) / total_days * (total_days - days)
                        
            elif asset.method == 'degressive':
                amount = residual_amount * asset.method_progress_factor
                if asset.prorata:
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * (total_days - days)
        return amount

    def _compute_board_undone_dotation_nb(self, cr, uid, asset, depreciation_date, total_days, context=None):
        if asset.depreciation_frequency == 'monthly':
            undone_dotation_number = asset.category_id.useful_life_years * asset.method_period         
        else:            
            undone_dotation_number = asset.category_id.useful_life_years
        if asset.method_time == 'end':
            end_date = datetime.strptime(asset.method_end, '%Y-%m-%d')
            undone_dotation_number = 0
            while depreciation_date <= end_date:
                depreciation_date = (datetime(depreciation_date.year, depreciation_date.month, depreciation_date.day) + relativedelta(months=+asset.method_period))
                undone_dotation_number += 1
        if asset.prorata:
            undone_dotation_number += 1
        return undone_dotation_number

    def compute_depreciation_board(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        currency_obj = self.pool.get('res.currency')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.value_residual == 0.0:
                continue
            posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_check', '=', True)],order='depreciation_date desc')
            old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)

            amount_to_depr = residual_amount = asset.value_residual
            if asset.prorata:
                depreciation_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
            else:
                # depreciation_date = 1st January of purchase year
                purchase_date = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
                #if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if (len(posted_depreciation_line_ids)>0):
                    last_depreciation_date = datetime.strptime(depreciation_lin_obj.browse(cr,uid,posted_depreciation_line_ids[0],context=context).depreciation_date, '%Y-%m-%d')
                    if asset.depreciation_frequency == 'monthly':
                        depreciation_date = (last_depreciation_date+relativedelta(months=+1))
                    else:
                        depreciation_date = (last_depreciation_date+relativedelta(months=+asset.method_period))                                                
                else:
                    depreciation_date = datetime(purchase_date.year, 1, 1)
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb(cr, uid, asset, depreciation_date, total_days, context=context)
            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                i = x + 1
                amount = self._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)
                company_currency = asset.company_id.currency_id.id
                current_currency = asset.currency_id.id
                # compute amount into company currency
                amount = currency_obj.compute(cr, uid, current_currency, company_currency, amount, context=context)
                residual_amount -= amount
                vals = {
                     'amount': amount,
                     'asset_id': asset.id,
                     'sequence': i,
                     'name': str(asset.id) +'/' + str(i),
                     'remaining_value': residual_amount,
                     'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                     'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                }
                depreciation_lin_obj.create(cr, uid, vals, context=context)
                # Considering Depr. Period as months
                if asset.depreciation_frequency == 'monthly':
                    depreciation_date = (datetime(year, month, day) + relativedelta(months=+1))
                    month = depreciation_date.month
                    day = depreciation_date.day
                    year = depreciation_date.year
                else:            
                    depreciation_date = (datetime(year, month, day) + relativedelta(months=+asset.method_period))
                    day = depreciation_date.day
                    month = depreciation_date.month
                    year = depreciation_date.year
                
        return True
    

