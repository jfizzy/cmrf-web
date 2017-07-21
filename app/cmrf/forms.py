from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, IntegerField, SelectField, TextAreaField, SelectMultipleField, RadioField
from wtforms.validators import Required, Optional, Length, Email, Regexp, EqualTo, URL
from wtforms.widgets import TextArea, ListWidget, CheckboxInput, FileInput
from wtforms import ValidationError
from ..models import User, Role, WorkOrder, Person
from .. import documents, photos

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
			
class MultiCheckboxField(SelectMultipleField):
	widget = ListWidget(prefix_label=False)
	option_widget = CheckboxInput()

class RequestForm(Form):
	title = StringField('Title', validators=[Required(), Length(6, 64)])
	desc = StringField('Description', validators=[Required(), Length(0, 200)], widget=TextArea())
	no_samples = IntegerField('Number of Samples', \
							 validators=[Required()])
	tm = MultiCheckboxField('Target Metabolites (Select all that apply)', \
							choices=[(0, 'Central Carbon Metabolism'), \
									  (1,'Peptides'), (2, 'Fatty Acids'), \
									  (3, 'Amino Acids'), (4, 'Other')], \
							default=[0], \
							coerce=int)
	other_tm = StringField('Other Target Metabolites (If applicable)', \
						   validators=[Optional(), Length(4, 20)])
	ri = MultiCheckboxField('Required Instruments (Select all that apply)', \
							 choices=[(0, 'QE-HF'), (1, 'QE-Basic'), \
							 		  (2,'TSQ'), (3, 'Unknown')], \
							 default=[3], coerce=int)
	assistance = RadioField('Assistance (Lab Technician)', \
							choices=[(0, 'Assistance Required'), (1, 'No Assistance Required')], \
							default=[0], coerce=int)

	submit = SubmitField("Submit")

class ReportForm(Form):
    balance = StringField('Balance For Request ($):', validators=[Required(), Length(2,20), Regexp('^[0-9]*$', 0, 'Must be an Integer')])
    desc = StringField('Notes', validators=[Required(), Length(0, 200)], widget=TextArea())
    file_loc = StringField('File Location (Results)', validators=[Optional()])

    submit = SubmitField("Submit")
	
class NewsItemForm(Form):
	title = StringField('Title', validators=[Required(), Length(6, 64)])
	desc = StringField('Description', validators=[Required(), Length(0, 2000)], widget=TextArea())
	url = StringField('URL', validators=[Optional(), URL(require_tld=False, message='Please enter a valid URL.')])
	
	submit = SubmitField("Submit")
	
class PublicationForm(Form):
	title = StringField('Title', validators=[Required(), Length(6,200)])
	desc = StringField('Description', validators=[Required(), Length(0, 2000)], widget=TextArea())
	file = FileField('PDF', validators=[FileRequired(), FileAllowed(documents, 'Only PDFs may be uploaded.')])
	
	submit = SubmitField("Submit")
	
class PersonForm(Form):
	name = StringField('Name', validators=[Required(), Length(6, 64)])
	title = StringField('Title', validators=[Required(), Length(6, 64)])
	email = StringField('Email (Optional)', validators=[Length(1, 64), Email(), Unique(Person, Person.email, 'Email already added to other Person')])
	file = FileField('Photo (png, jpg, gif) (Optional) ', validators=[FileAllowed(photos, 'Only images of approved types may be uploaded.')])
	
	submit = SubmitField("Submit")

class AdminChangeRequest(Form):
    title = StringField('Title', validators=[Required(), Length(6, 64)])
    desc = StringField('Description', validators=[Required(), Length(0, 200)], widget=TextArea())
    no_samples = IntegerField('Number of Samples', \
							 validators=[Required()])
    tm = SelectMultipleField('Target Metabolites (Select all that apply)', \
                                                                   choices=[(0, 'Central Carbon Metabolism'), \
                                                                            (1,'Peptides'), (2, 'Fatty Acids'), \
                                                                            (3, 'Amino Acids'), (4, 'Other')], \
                                                                   default=[0], \
                                                                   coerce=int)
    other_tm = StringField('Other Target Metabolites (If applicable)', \
                                                                 validators=[Optional(), Length(4, 20)])
    ri = SelectMultipleField('Required Instruments (Select all that apply)', \
                                                                   choices=[(0, 'QE-HF'), (1, 'QE-Basic'), \
                                                                            (2,'TSQ'), (3, 'Unknown')], \
                                                                   coerce=int)
    assistance = RadioField('Assistance (Technician)', \
                                                                  choices=[(0, 'Assistance Required (Technician)'), (1, 'No Assistance Required')], \
                                                                  default=[0], coerce=int)
                                          
    submit = SubmitField("Submit")

def __init__(self, fa, wo, *args, **kwargs):
    super(AdminChangeRequest, self).__init__(*args, **kwargs)
    self.fa = fa
    self.wo = wo
