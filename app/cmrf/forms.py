from flask_wtf import Form
from wtforms import StringField, SubmitField, IntegerField, SelectField, TextAreaField, SelectMultipleField, RadioField
from wtforms.validators import Required, Optional, Length, Email, Regexp, EqualTo
from wtforms.widgets import TextArea
from wtforms import ValidationError
from ..models import User, Role, WorkOrder

class Unique(object):
	""" validator that checks field uniqueness """
	def __init__(self, model, field, message=None):
		self.model = model
		self.field = field
		if not message:
			message = u'This element already exists'
		self.message = message

	def __call__(self, form, field):
		check = self.model.query.filter(self.field == field.data).first()
		if check:
			raise ValidationError(self.message)

class RequestForm(Form):
	title = StringField('Title', validators=[Required(), Length(6, 64)])
	desc = StringField('Description', validators=[Required(), Length(0, 200)], widget=TextArea())
	no_samples = SelectField('Number of Samples', \
							 validators=[Required()], \
							 choices=[(100,'100'),(200,'200'),(300,'300'), \
								      (400,'400'),(500,'500'),(600,'600'), \
									  (700,'700'),(800,'800'),(900,'900'), \
									  (1000,'1000')], coerce=int)
	tm = SelectMultipleField('Target Metabolites (Select all that apply)', \
							 choices=[(0, 'Central Carbon Metabolism'), \
							 		  (1,'Peptides'), (2, 'Fatty Acids'), \
									  (3, 'Amino Acids'), (4, 'Other')], \
							 default=[0], \
							 coerce=int)
	other_tm = StringField('Other Target Metabolites (If applciable)', \
						   validators=[Optional(), Length(4, 20)])
	ri = SelectMultipleField('Required Instruments (Select all that apply)', \
							 choices=[(0, 'QE-HF'), (1, 'QE-Basic'), \
							 		  (2,'TSQ'), (3, 'Unknown')], \
							 coerce=int)
	funding_acc_num = StringField('UC Funding Account #', \
								   validators=[Required(), \
								   			   Length(6,20), \
										   	   Regexp('^[0-9]*$', 0, 'Must be an Integer')])
	funding_acc_type = RadioField(choices=[(0, 'NSPRC'), (1, 'CIHR'), \
										   (2, 'Provincial'), (3, 'Other')], \
								  validators=[Required()], coerce=int)
	funding_acc_other = StringField('Other Account Type (If applciable)', \
									validators=[Optional(), Length(4,20)])
	assistance = RadioField('Assistance (Technician)', \
							choices=[(0, 'Assistance Required (Technician)'), (1, 'No Assistance Required')], \
							default=[0], coerce=int)

	submit = SubmitField("Submit")
