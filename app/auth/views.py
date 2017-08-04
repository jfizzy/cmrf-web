from flask import render_template, redirect, request, url_for, flash, g, jsonify
from flask_login import login_user, logout_user, login_required, current_user, confirm_login, fresh_login_required, login_fresh
from flask_httpauth import HTTPBasicAuth
from urllib import unquote
from ..decorators import admin_required, user_acc_required
from . import auth
from .. import db
from ..models import User, Role, AnonymousUser, WorkOrder
from ..email import send_email
from .forms import LoginForm, ReAuthForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm, ChangeAccountDetailsForm,\
    ChangeAccountDetailsAdminForm

httpauth = HTTPBasicAuth()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and h_verify_password(user.email, form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next:
                return redirect(next)
            else:
                return redirect(url_for('cmrf.index'))
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/reauthenticate', methods=['GET', 'POST'])
def reauthenticate():
    form = ReAuthForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and h_verify_password(user.email, form.password.data):
            confirm_login() #marks the user session as fresh
            next = request.args.get('next')
            if next:
                return redirect(next)
            else:
                return redirect(url_for('cmrf.index'))
        flash('Invalid email or password.')
    return render_template('auth/reauthenticate.html', form=form)    

@httpauth.verify_password
def h_verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email = email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user=User(UCID=int(form.UCID.data),first_name=form.first_name.data,last_name=form.last_name.data,password=form.password.data,
						email=form.email.data,lab=form.lab.data,phone=str(form.phone.data))
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        g.current_user = user
        login_user(user)
        flash('Thanks for registering! Please click the link in the email we just sent you in order to confirm your account.')
        return redirect(url_for('cmrf.index'))
    else:
        return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.email_conf:
        return redirect(url_for('cmrf.index'))
    if current_user.confirm_email(token):
        flash('Thanks for confirming your account! You may now access your user features.')
    else:
		flash('That confirmation link is invalid or has expired.')
    return redirect(url_for('cmrf.index'))

@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		if not current_user.email_conf:
			if request.endpoint[:5] == 'auth.' or request.endpoint[:5] == 'cmrf.':
				if request.endpoint != 'auth.unconfirmed' and request.endpoint != 'cmrf.index' and request.endpoint != 'auth.logout' and request.endpoint[:12] != 'auth.confirm' and request.endpoint != 'auth.resend_confirmation':
					return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.email_conf:
		return redirect('main.index')
	return render_template('auth/unconfirmed.html')

@auth.route('/send-confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	print token
	send_email(current_user.email, 'Confirm Your Account',
			   'auth/email/confirm', user=current_user, token=token)
	flash('A new confirmation email has been sent to you by email.')
	return redirect(url_for('cmrf.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@fresh_login_required
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

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_req.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        print 'GOT HERE'
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form, token=token)

@auth.route('/change-email', methods=['GET', 'POST'])
@fresh_login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change-email/<token>')
@fresh_login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))

@auth.route('/account', methods=['GET'])
@login_required
@fresh_login_required
def account_details():
    return render_template("auth/account.html")

@auth.route('/account/<int:id>', methods=['GET'])
@fresh_login_required
@admin_required
def adm_account_details(id):
    user = User.query.get_or_404(id)
    return render_template("auth/adm_account.html", selected_user=user)

@auth.route('/change-account', methods=['GET','POST'])
@fresh_login_required
def change_account_details():
    form = ChangeAccountDetailsForm(lab=current_user.lab, phone=current_user.phone)    
    if form.validate_on_submit():
        current_user.lab = form.lab.data
        current_user.phone = form.phone.data
        db.session.add(current_user)
        flash('Your information was successfully updated.')
        return redirect(url_for('auth.account_details'))
    return render_template("auth/change_account.html", form=form)

@auth.route('/change-account/<int:id>', methods=['GET','POST'])
@fresh_login_required
@user_acc_required
def adm_change_account_details(id):
    user = User.query.get_or_404(id)
    form = ChangeAccountDetailsAdminForm(user=user)
    if form.validate_on_submit():
        if form.first_name.data != None and \
            user.first_name != form.first_name.data:
            user.first_name = form.first_name.data
        if form.last_name.data != None and \
            user.last_name != form.last_name.data:
            user.last_name = form.last_name.data
        user.email = form.email.data
        user.email_conf = form.email_conf.data
        user.role = Role.query.get(form.role.data)
        if user.lab != form.lab.data:
            user.lab = form.lab.data
        if user.phone != form.phone.data:
            user.first_name = form.first_name.data
        db.session.add(user)
        flash('User account has been updated.')
        return redirect(url_for('auth.adm_account_details', id=user.id))
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.email.data = user.email
    form.email_conf.data = user.email_conf
    form.role.data = user.role_id
    form.lab.data = user.lab
    form.phone.data = user.phone
    return render_template("auth/adm_change_account.html", form=form, selected_user=user)

@auth.route('/all-accounts', methods=['GET'])
@fresh_login_required
@user_acc_required
def all_accounts():
    users = User.query.all()
    return render_template("auth/adm_all_accounts.html", users=users)
	
@auth.route('/delete-account/<int:id>', methods=['GET'])
@fresh_login_required
@admin_required
def delete_account(id):
	user = User.query.get_or_404(id)
	requests = WorkOrder.query.filter_by(RSC_ID=id).all()
	for request in requests:
		db.session.delete(request)
	db.session.delete(user)
	db.session.commit()
	flash('User Deleted as well as their Requests.')
	return redirect(url_for('auth.all_accounts'))
