from openerp.osv import osv, fields


class brief_form(osv.osv):
    _name = "brief.form"
    _description = "Brief Form "
    _columns={
        'background': fields.text('Background?', size=16),
        'issue': fields.text('Issue', size=16),
        'selling': fields.text('What are we selling?', size=16),                  
        'objective': fields.text('What do we want to accomplish? The Objective?', size=16),                  
        'connect': fields.text('With whom do we want to connect?', size=16),                  
        'big_insights': fields.text('What do they currently think/feel? The big insights', size=16),                  
        'tagline': fields.text('Tagline', size=16),                  
        'feel': fields.text('What do we want them to feel?', size=16),                  
        'like': fields.text('What would they like about this?', size=16),                  
        'different': fields.text('How will this be different from others?', size=16),                                    
        'guidelines': fields.text('Creative guidelines/tone?', size=16),                                    
        'persuasive_idea': fields.text('What is the single most persuasive idea that we can convey?', size=16),                                    
        'conclusion': fields.text('Conclusion', size=16),                                    
              }

    def brief_form_done(self, cr, uid, ids, context=None):
        return True
