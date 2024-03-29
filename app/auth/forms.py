from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.fields.html5 import TelField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, NumberRange
from wtforms import ValidationError
from ..models import User, Role




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

class LoginForm(Form):
    email = StringField('Email address', validators=[Required(), Length(4, 64), Email()])
    password = PasswordField('Password', validators=[Required(), Length(4, 64)])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')

class ReAuthForm(Form):
    email = StringField('Email', validators=[Required(), Length(4, 64), Email()])
    password = PasswordField('Password', validators=[Required(), Length(4, 64)])
    submit = SubmitField('Authenticate')
    
class RegistrationForm(Form):
    UCID = StringField('UCID', validators=[Required(), Length(min=8,max=8),
                                            Regexp('^[0-9]*$', 0,
                                            'Must be an 8 digit integer'),
                                            Unique(User, User.UCID, 'UCID already registered')])
    first_name = StringField('First Name', validators=[Required(), Length(2,64),
                                                            Regexp('^[A-Za-z -]*$', 0,
                                                            'Name contains invalid characters')])
    last_name = StringField('Last Name', validators=[Required(), Length(2,64),
                                                        Regexp('^[A-Za-z -]*$', 0,
                                                        'Name contains invalid characters')])
    email = StringField('Email', validators=[Required(), Length(1, 64), Email(), Unique(User, User.email, 'Email already registered')])
    password = PasswordField('Password', validators=[Required(), Length(6,64), EqualTo('password_confirm', message='Passwords do not match')])
    password_confirm = PasswordField('Confirm Password', validators=[Required()])
    pi_fname = StringField('First Name', validators=[Required(), Length(2,64)])
    pi_lname = StringField('Last Name', validators=[Required(), Length(2,64)])
    phone = TelField('Phone Number (Optional)')
    
    submit = SubmitField('Register')

class ChangePasswordForm(Form):
	old_password = PasswordField('Current Password', validators=[Required()])
	password = PasswordField('New Password', validators=[Required()])
	password_confirm = PasswordField('Confirm New Password', validators=[Required(),
									 EqualTo('password', message='Passwords do not match')])
	submit = SubmitField('Update Password')

class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        Required(), EqualTo('password_confirm', message='Passwords do not match')])
    password_confirm = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[Required(), Length(1, 64),
                                                 Email(),
												 Unique(User, User.email, 'Email already registered')])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class ChangeAccountDetailsForm(Form):
    pi_fname = StringField('First Name', validators=[Required(), Length(2,64)])
    pi_lname = StringField('Last Name', validators=[Required(), Length(2,64)])
    phone = TelField('Phone Number')
    submit = SubmitField('Update')

class ChangeAccountDetailsAdminForm(Form):
    first_name = StringField('First Name', validators=[Required(), Length(2,64),
                                                       Regexp('^[A-Za-z -]*$', 0,
                                                       'Name contains invalid characters')])
    last_name = StringField('Last Name', validators=[Required(), Length(2,64),
                                                     Regexp('^[A-Za-z -]*$', 0,
                                                     'Name contains invalid characters')])
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    email_conf = BooleanField('Confirmed')
    
    role = SelectField('User Role', coerce=int)
    pi_fname = StringField('First Name', validators=[Required(), Length(2,64)])
    pi_lname = StringField('Last Name', validators=[Required(), Length(2,64)])
    phone = TelField('Phone Number (Optional)')

    submit = SubmitField('Confirm Changes')
    
    def __init__(self, *args, **kwargs):
        super(ChangeAccountDetailsAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Email already Registered.')