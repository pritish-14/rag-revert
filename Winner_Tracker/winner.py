# coding: utf-8
# Copyright 2014-2015 - Apagen Solutions Pvt. Ltd.
from openerp.osv import osv, fields
from datetime import datetime


class Winner(osv.osv):
    _name = "winner"
    _columns = {
        'name': fields.char('Name'),
        'promotion': fields.char('Promotion'),
        'promotion_date': fields.date('Promotion Date'),
        'show': fields.many2one('show.entry','Show'),
        'presenter': fields.many2one('res.users', 'Presenter'),
        'prize_won': fields.many2one('prize.entry','Prize Won'),
        'telephone': fields.char('Telephone'),
        'id_no': fields.char('Identification No'),
        'creation_date': fields.datetime('Creation Date'),
        'state': fields.selection([('unclaimed', 'Unclaimed'),
                                    ('claimed', 'Claimed'),('nowinner', 'No Winner')], 'Status'),
        'claim_date': fields.datetime('Claim Date'),
        'no_winner': fields.boolean('No Winner'),
        'brand_id': fields.many2one('brand', 'Station', required=1),
        }
    _defaults = {
        'creation_date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'promotion_date': fields.date.context_today,
        'presenter': lambda obj, cursor, user, context: user,
        'state': "unclaimed",
    }
    
    '''def onchange_no_win(self, cr, uid, ids, context=None):
    	list_ids = self.browse(cr, uid, ids, context)
    	print ">>>>>>>>>", list_ids
    	print "2222222222222", list_ids.no_winner
        for data in list_ids:
			print "...........", data.no_winner
        return True'''
    
    '''def onchange_no_win(self, cr, uid, no_winner, context=None):
    	print "222222222222222222", context
    	print "00000000000000000000", no_winner
        if context == True:
            journal = self.browse(cr, uid, no_winner)
            print "llllllllllllllllllllllll", journal
            return {
                'value': {
                    'state': 'nowinner',
                }
            }'''
        #return True
    
    def unclaimed(self, cursor, user, ids, context=None):
        return True
    
    def claim(self, cr, uid, ids, context=None):
    	self.write(cr, uid, ids, {'state': 'claimed', 'claim_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        return True   

    def no_winner(self, cr, uid, ids, context=None):
    	self.write(cr, uid, ids, {'state': 'nowinner'})
        return True 
#	def claimed(self, cr, uid, ids):
		#self.write(cr, uid, ids, { 'state' : 'claimed' })
#        return True

    '''def no_winner(self, cr, uid, ids):
        self.write(cr, uid, ids, { 'state' : 'nowinner' })
        return True'''
        
    
class prize_claim(osv.osv):
    _name = "prize.claim"

    def action_claim(self, cursor, user, ids, context=None):
        winner_obj = self.pool.get('winner')
        for winner_id in winner_obj.browse(cursor, user, context['active_ids']):
            print "idddddddd", winner_id
            print "idddddddd", winner_id.id
            print "idddddddd", winner_id.name
            if (winner_id.state == 'unclaimed'):
                winner_obj.write(cursor, user, [winner_id.id], {'state': 'claimed', 'claim_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        return True
        
class Show(osv.osv):
    _name = "show.entry"
    _rec_name = 'show_name'
    _columns = {
    'show_name': fields.char('Show Name'),
    }
    
class Prize(osv.osv):
    _name = "prize.entry"
    _rec_name = 'prize_name'
    _columns = {
    'prize_name': fields.char('Prize Name'),
    }
