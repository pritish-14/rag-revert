from openerp.osv import osv, fields
from datetime import date
from datetime import datetime
import re
from dateutil.relativedelta import relativedelta


class hr_employee(osv.osv):
    _inherit = 'hr.employee'

    def name_get(self, cr, uid, ids, context=None):
        # always return the full hierarchical name
        res = self._complete_name(cr, uid, ids, 'complete_name', None, context=context)
        return res.items()

    def _complete_name(self, cr, uid, ids, name, args, context=None):
        """ Forms complete name of Employee from First and Last name
        @return: Dictionary of values
        """
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            if m.surname:
                surname = m.surname
            else:
                surname = ''
            res[m.id] = m.name + ' ' + surname
        return res
    
    _columns = {
        'name_related': fields.related('resource_id', 'name', type='char', string='First &amp; Middle Name', readonly=True, store=True),
        'surname': fields.char('Surname', size=32),
        #'name' : fields.char("First & Middle Name"),
        'job_id': fields.many2one('hr.job', 'Job Title'),
        'employment_type':  fields.selection([('permanent', "Permanent"),
                                              ('contractual', "Contractual"),
                                              ('freelancer', "Freelancer"),
                                              ('correspondent', "Correspondent"),
                                              ('trainee', "Trainee"),
                                              ('intern', "Intern")],
                                             "Employment Type"),
        'employment_date':fields.date('Employment Date'),
        'manager': fields.boolean('Is a Manager'),
        'exit_date': fields.date('Exit Date'),
        'staff_no': fields.integer('Staff No.'),
        'marital':  fields.selection([('single', "Single"),
                                              ('married', "Married"),
                                              ('separated', "Separated"),
                                              ('divorced', "Divorced"),
                                              ('widowed', "Widowed")],
                                             "Marital Status"),
       'section': fields.many2many('dep.section', 'r_id','p_id','c_id','Section'),
       'nssf_no': fields.char('NSSF No', size=32),
       'nhif_no': fields.char('NHIF No', size=32),
       'pin_no': fields.char('PIN No', size=32),
       'district': fields.char('District', size=32),
       'division': fields.char('Division', size=32),
       'location': fields.char('Location', size=32),
       'sub_location': fields.char('Sub-Location', size=32),
       'village_market': fields.char('Village/Market', size=32),
       'permanent_address': fields.char('Permanent Address'),
       'age':fields.char('Age',readonly=True),
       'bank_account_id': fields.many2one('res.partner.bank', 'Bank Account No', domain="[('partner_id','=',address_home_id)]", help="Employee bank salary account"), 
       'vehicle_distance': fields.integer('Home-Work Distance(in meters)', help="In meters", invisible="1"),
        'address_home_id': fields.many2one('res.partner', 'Residential Address'),
    }

    def onchange_employment(self, cr, uid, ids, employment_type, gender, context=None):
        value1 = []
        if employment_type == 'permanent' and gender == 'male' and not gender == 'female':
            category_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Permanent')])
            gender_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Male')])            
            if category_id:
                value1.append(category_id[0])
                if gender_id:
                    value1.append(gender_id[0])                
            else:
                category_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Permanent'},context=context)                  
                value1.append(category_id)                           
                gender_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Male'},context=context)                  
                value1.append(gender_id)                           
        elif employment_type == 'permanent' and gender == 'female' and not gender == 'male' :
            category_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Permanent')])
            gender_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Female')])            
            if category_id:
                value1.append(category_id[0])
                if gender_id:
                    value1.append(gender_id[0])                
            else:
                category_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Permanent'},context=context)                  
                value1.append(category_id)                           
                gender_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Male'},context=context)                  
                value1.append(gender_id)                           
        elif employment_type == 'permanent' and not gender == 'male' and not gender == 'female':
            category_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Permanent')])
            if category_id:
                value1.append(category_id[0])
            else:
                category_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Permanent'},context=context)                  
                value1.append(category_id)                           
        return {'value' : {'category_ids': value1 }}

    def onchange_gender(self, cr, uid, ids, gender, employment_type, context=None):
        value1 = []
        if gender == 'male' and employment_type == 'permanent':
            category_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Male')])
            emp_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Permanent')])            
            if category_id:
                value1.append(category_id[0])
                if emp_id:
                    value1.append(emp_id[0])                
            else:
                category_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Male'},context=context)                  
                value1.append(category_id)                           
                emp_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Permanent'},context=context)                  
                value1.append(emp_id)                           
        elif gender == 'male' and not employment_type == 'permanent':
            category_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Male')])
            if category_id:
                value1.append(category_id[0])
            else:
                category_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Male'},context=context)                  
                value1.append(category_id)                           
        
        if gender == 'female' and employment_type == 'permanent':
            category_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Female')])
            emp_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Permanent')])                        
            if category_id:
                value1.append(category_id[0])
                if emp_id:
                    value1.append(emp_id[0])                
            else:
                category_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Female'}, context=context)                      
                value1.append(category_id)  
                emp_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Permanent'},context=context)                  
                value1.append(emp_id)                           
        elif gender == 'female' and not employment_type == 'permanent':
            category_id = self.pool.get('hr.employee.category').search(cr, uid, [('name','=','Female')])
            if category_id:
                value1.append(category_id[0])
            else:
                category_id = self.pool.get('hr.employee.category').create(cr,uid,{'name' : 'Female'},context=context)                  
                value1.append(category_id)                           
                
        return {'value' : {'category_ids': value1 }}
    
    def onchange_department_id(self, cr, uid, ids, department_id, context=None):
        value1 = []
        if department_id:
            department = self.pool.get('hr.department').browse(cr, uid, department_id)
            for data in department.section_ids:
                value1.append(data.id)
            print"---------------", value1
            if department_id=="":
            	value1=""
        return {'value' : {'section':value1 }}
       
    
    def onchange_getage_id(self,cr,uid,ids,dob,context=None):
        age = ''
        now = datetime.now()
        if dob:
            dob = datetime.strptime(str(dob), '%Y-%m-%d')
            delta = relativedelta(now, dob)
            deceased = ''
            years_months_days = str(delta.years) + 'year ' \
                    + str(delta.months) + 'month '
            val = {
	            'age':	years_months_days,
	            }
            return {'value': val}                    
        else:
            years_months_days = 'No DoB !'

        # Return the age in format y m d when the caller is the field name
            val = {
	            'age':	years_months_days,
	            }
            return {'value': val}
'''     if dob:
        current_date=datetime.datetime.now()
        current_year=current_date.year
        current_month=current_date.month
        birth_date = parser.parse(dob)
        x=birth_date.month
        y=current_month
        if x>y:
        	y=y+12
        	current_year=current_year-1
        	current_age=(current_year-birth_date.year)*12
        	month_1=y-x
        	total_age_months=current_age+month_1
        	val = {
           		'age' :	total_age_months,
           		}
        	return {'value': val}
        else:
        	current_age=(current_year-birth_date.year)*12
        	month_1=y-x
        	total_age_months=current_age+month_1
        	val = {
           		'age':	total_age_months,
           		}
        	return {'value': val}'''
    
    
class hr_department(osv.osv):
    _description = "Department"
    _inherit = 'hr.department'
    _columns = {
        'approved_head_count': fields.integer('Approved Head Count'),
        'section_ids': fields.one2many('dep.section', 'sec_id', 'Sections'),
    }

    def copy_data(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        default['section_ids'] = []
        return super(hr_department, self).copy_data(cr, uid, ids, default, context=context)

    def _get_members(self, cr, uid, context=None):
        mids = self.search(cr, uid, [('manager_id', '=', uid)], context=context)
        result = {uid: 1}
        for m in self.browse(cr, uid, mids, context=context):
            for user in m.section_ids:
                result[user.id] = 1
        return result.keys()
        
        
        
        
class department_section(osv.osv):
    _name = 'dep.section'
    
    _columns = {
        'sec_id': fields.many2one('hr.department', 'Section'),
        'name': fields.char("Name",required=True),
        'sec_manager': fields.many2one("hr.employee","Section Manager"),
    }
    

