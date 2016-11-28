from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('cmrf.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
	
@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(UCID=int(form.UCID.data),
					first_name=form.first_name.data,
					last_name=form.last_name.data,
					password=form.password.data,
					email=form.email.data,
					phone=form.phone.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, 'Confirm Your Account',
				   'auth/email/confirm', user=user, token=token)
		flash('Thanks for registering. Please confirm your account by clicking the link in the email we just sent.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html',form=form)
	
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.email_conf:
		return redirect(url_for('cmrf.index'))
	if current_user.confirm_email(token):
		flash('Thanks for confirming your account! You may now login.')
	else:
		flash('That confirmation link is invalid or has expired.')
	return redirect(url_for('cmrf.index'))
	
@auth.before_app_request
def before_request():
	if current_user.is_authenticated \
		and not current_user.email_conf \
		and request.endpoint[:5] != ('auth.' or 'cmrf.'):
		return redirect(url_for('auth.unconfirmed'))
		
@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.email_conf:
		return redirect('main.index')
	return render_template('auth/unconfirmed.html')
	
@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, 'Confirm Your Account',
			   'auth/email/confirm', user=current_user, token=token)
	flash('A new confirmation email has been sent to you by email.')
	return redirect(url_for('main.index'))
	
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			flash('Your password was successfully updated.')
			return redirect(url_for('cmrf.index'))
		else:
			flash('Invalid password.')
	return render_template("auth/change_password.html", form=form)