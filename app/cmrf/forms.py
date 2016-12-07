from flask_wtf import Form
from wtforms import StringField, SubmitField, IntegerField, SelectField, TextAreaField, SelectMultipleField, RadioField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
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
    desc = TextAreaField('Description', validators=[Required(), Length(0, 200)])
    #no_samples = SelectField('Number of Samples', validators=[Required()], choices=['100','200','300','400','500','600','700','800','900','1000'])
    #tm = SelectMultipleField('Target Metabolites', validators=[Required()], choices=['Peptides', 'Fatty Acids', 'Amino Acids', 'Other'])
    #ri = SelectMultipleField('Required Instruments', validators=[Required()], choices=['QE-HF', 'QE-Basic', 'TSQ', 'Unknown'])
    #funding will go here
    assistance = RadioField('Assistance (Technician)', choices=[(True, 'Yes'), (False, 'No')])
    submit = SubmitField("Submit")
