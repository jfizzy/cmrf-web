from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from ..decorators import admin_required, all_r_required
from ..models import WorkOrder, User, Permission
from . import cmrf

@cmrf.route('/', methods=['GET'])
def index():
	return render_template('cmrf/cmrf.html')

@cmrf.route('/requests', methods=['GET'])
@login_required
def requests():
	requests = WorkOrder.query.filter_by(
					RSC_ID=current_user.UCID).order_by(
					WorkOrder.submit_date.desc())
	return render_template('cmrf/user_requests.html', requests=requests)

@cmrf.route('/request/<int:id>', methods=['GET'])
@login_required
def request(id):
	request = WorkOrder.query.filter_by(ID=str(id)).first_or_404()
	if current_user.id != request.RSC_ID:
		if not current_user.can(Permission.ALL_R):
			abort(404)
	user = User.query.filter_by(UCID=request.RSC_ID).first()
	return render_template('cmrf/request.html', request=request, owner=user)

@cmrf.route('/all-requests')
@login_required
@all_r_required
def all_requests():
	requests = WorkOrder.query.join(User,
						 WorkOrder.RSC_ID==User.UCID).add_columns(
						 WorkOrder.ID, WorkOrder.RSC_ID, User.first_name,
						 User.last_name, WorkOrder.title, WorkOrder.submit_date,
						 WorkOrder.no_samples, WorkOrder.status).order_by(
						 WorkOrder.submit_date.desc()).all()
	return render_template('cmrf/all_requests.html',
						   title=None,requests=requests)

@cmrf.route('/all-approved-requests')
@login_required
@all_r_required
def all_active_requests():
	requests = WorkOrder.query.filter_by(
					status='Approved').order_by(
					WorkOrder.submit_date.desc())
	return render_template('cmrf/all_requests.html',
						   title='Approved', requests=requests)

@cmrf.route('/all-pending-requests')
@login_required
@all_r_required
def all_pending_requests():
	requests = WorkOrder.query.filter_by(
					status='Pending').order_by(
					WorkOrder.submit_date.desc())
	return render_template('cmrf/all_requests.html',
						   title='Pending Approval', requests=requests)

@cmrf.route('/all-completed-requests')
@login_required
@all_r_required
def all_completed_requests():
	requests = WorkOrder.query.filter_by(
					status='Complete').order_by(
					WorkOrder.submit_date.desc())
	return render_template('cmrf/all_requests.html',
						   title='Completed', requests=requests)

@cmrf.route('/all-declined-requests')
@login_required
@all_r_required
def all_declined_requests():
	requests = WorkOrder.query.filter_by(
					status='Declined').order_by(
					WorkOrder.submit_date.desc())
	return render_template('cmrf/all_requests.html',
						   title='Declined', requests=requests)
