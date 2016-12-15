from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from ..decorators import admin_required, all_r_required, view_r_required, make_r_required, user_acc_required
from ..models import WorkOrder, User, Permission, FundingAccount, Report
from . import cmrf
from .. import db
from .forms import RequestForm, ReportForm

@cmrf.route('/', methods=['GET'])
def index():
	return render_template('cmrf/cmrf.html')

@cmrf.route('/requests', methods=['GET'])
@login_required
@view_r_required
def requests():
	requests = WorkOrder.query.filter_by(
					RSC_ID=current_user.UCID).order_by(
					WorkOrder.submit_date.desc())
	return render_template('cmrf/user_requests.html', requests=requests)

@cmrf.route('/adm-requests/<int:id>')
@login_required
@all_r_required
@user_acc_required
def adm_requests(id):
    requests = WorkOrder.query.filter_by(
                    RSC_ID=id).order_by(
                    WorkOrder.submit_date.desc())
    return render_template('cmrf/adm_requests.html', requests=requests)

@cmrf.route('/request/<int:id>', methods=['GET'])
@login_required
@view_r_required
def request(id):
	request = WorkOrder.query.filter_by(ID=str(id)).first_or_404()
	if current_user.id != request.RSC_ID:
		if not current_user.can(Permission.ALL_R):
			abort(404)
	user = User.query.filter_by(UCID=request.RSC_ID).first()
	return render_template('cmrf/request.html', request=request, owner=user)

@cmrf.route('/make-request', methods=['GET', 'POST'])
@login_required
@make_r_required
def make_request():
	userfa = FundingAccount.query.filter_by(RSC_ID=current_user.id).first()
	form = RequestForm()
	if form.validate_on_submit():
		fa = FundingAccount(int(form.funding_acc_num.data), form.funding_acc_type.data, current_user.id, form.funding_acc_other.data)
		if userfa is not None:
			userfa.acc_no = fa.acc_no
			userfa.acc_type = fa.acc_type
			userfa.acc_other = fa.acc_other
			db.session.add(userfa)
		else:
			db.session.add(fa)
		wo = WorkOrder(title=form.title.data, no_samples=form.no_samples.data, \
					   RSC_ID=current_user.UCID, desc=form.desc.data, \
					   tm=form.tm.data, ri=form.ri.data, assistance=form.assistance.data)

		db.session.add(wo)
		db.session.commit()
		flash('Request Submitted.')
		return redirect(url_for('cmrf.requests'))
	else:
		return render_template('cmrf/make_request.html', errors=form.errors.items(), form=form)

@cmrf.route('/approve-request/<int:id>', methods=['GET'])
@login_required
@all_r_required
def approve_request(id):
    wo = WorkOrder.query.get_or_404(id)
    wo.status = 'In Progress'
    wo.ADM_ID = current_user.UCID # for records
    db.session.add(wo)
    db.session.commit()
    flash('Request Approved.')
    return redirect(url_for('cmrf.request', id=wo.ID))

@cmrf.route('/cancel-request/<int:id>', methods=['GET'])
@login_required
@all_r_required
def cancel_request(id):
    wo = WorkOrder.query.get_or_404(id)
    wo.status = 'Cancelled'
    wo.ADM_ID = current_user.UCID # for records
    db.session.add(wo)
    db.session.commit()
    flash('Request Cancelled.')
    return redirect(url_for('cmrf.request', id=wo.ID))

@cmrf.route('/edit-request/<int:id>', methods=['GET', 'POST'])
@login_required
@user_acc_required
def edit_request(id):
    wo = WorkOrder.query.get_or_404(id)
    userfa = FundingAccount.query.filter_by(RSC_ID=current_user.id).first()
    form = RequestForm(fa=userfa, wo=wo)
    if form.validate_on_submit():
        fa = FundingAccount(int(form.funding_acc_num.data), form.funding_acc_type.data, current_user.id, form.funding_acc_other.data)
        if userfa is not None:
            userfa.acc_no = fa.acc_no
            userfa.acc_type = fa.acc_type
            userfa.acc_other = fa.acc_other
            db.session.add(userfa)
        else:
            db.session.add(fa)
        wo.title = form.title.data
        wo.no_samples = form.no_samples.data
        wo.desc = form.desc.data
        wo.tm = form.desc.data
        wo.assistance = form.assistance.data
        if 0 in form.tm.data:
            wo.tm_ccm = True
        if 1 in form.tm.data:
            wo.tm_pep = True
        if 2 in form.tm.data:
            wo.tm_fa = True
        if 3 in form.tm.data:
            wo.tm_aa = True
        if 4 in form.tm.data:
            wo.tm_oth = True
            wo.tm_oth_txt = form.other_tm.data

        if 0 in form.ri.data:
            wo.ri_qehf = True
        if 1 in form.ri.data:
            wo.ri_qeb = True
        if 2 in form.ri.data:
            wo.ri_tsq = True
        if 3 in form.ri.data:
            wo.ri_unk = True
        db.session.add(wo)
        db.session.commit()
        flash('Changes Saved.')
        return redirect(url_for('cmrf.adm_requests', id=wo.RSC_ID))
    form.title.data = wo.title
    form.no_samples.data = wo.no_samples
    form.desc.data = wo.desc
    form.funding_acc_num.data = userfa.acc_no
    form.funding_acc_other.data = userfa.acc_other
    form.assistance.data = wo.assistance
    return render_template("cmrf/edit_request.html", id=wo.RSC_ID, form=form)

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

@cmrf.route('/all-active-requests')
@login_required
@all_r_required
def all_active_requests():
        requests = WorkOrder.query.filter_by(status='In Progress').join(User,
                                     WorkOrder.RSC_ID==User.UCID).add_columns(
                                     WorkOrder.ID, WorkOrder.RSC_ID, User.first_name,
                                     User.last_name, WorkOrder.title, WorkOrder.submit_date,
                                     WorkOrder.no_samples, WorkOrder.status).order_by(
                                     WorkOrder.submit_date.desc()).all()
	return render_template('cmrf/all_requests.html',
						   title='In Progress', requests=requests)

@cmrf.route('/all-pending-requests')
@login_required
@all_r_required
def all_pending_requests():
	requests = WorkOrder.query.filter_by(status='Pending Approval').join(User,
                                     WorkOrder.RSC_ID==User.UCID).add_columns(
                                     WorkOrder.ID, WorkOrder.RSC_ID, User.first_name,
                                     User.last_name, WorkOrder.title, WorkOrder.submit_date,
                                     WorkOrder.no_samples, WorkOrder.status).order_by(
                                     WorkOrder.submit_date.desc()).all()
	return render_template('cmrf/all_requests.html',
						   title='Pending', requests=requests)

@cmrf.route('/all-complete-requests')
@login_required
@all_r_required
def all_complete_requests():
	requests = WorkOrder.query.filter_by(status='Complete').join(User,
                                     WorkOrder.RSC_ID==User.UCID).add_columns(
                                     WorkOrder.ID, WorkOrder.RSC_ID, User.first_name,
                                     User.last_name, WorkOrder.title, WorkOrder.submit_date,
                                     WorkOrder.no_samples, WorkOrder.status).order_by(
                                     WorkOrder.submit_date.desc()).all()
	return render_template('cmrf/all_requests.html',
						   title='Completed', requests=requests)

@cmrf.route('/all-cancel-requests')
@login_required
@all_r_required
def all_cancel_requests():
	requests = WorkOrder.query.filter_by(
					status='Cancel').order_by(
					WorkOrder.submit_date.desc())
	return render_template('cmrf/all_requests.html',
						   title='Cancelled', requests=requests)

@cmrf.route('/make-report/<int:id>', methods=['GET', 'POST'])
@login_required
@all_r_required
def make_report(id):
    wo = WorkOrder.query.get_or_404(id)
    form = ReportForm()
    if form.validate_on_submit():
        report = Report(int(form.balance.data), wo.ID, desc=form.desc.data, file_loc=form.file_loc.data)
        db.session.add(report)
        db.session.commit()
        wo.RPT_ID = report.ID
        wo.status = 'Complete'
        db.session.add(wo)
        db.session.commit()
        flash('Report Submitted Successfully.')
        return redirect(url_for('cmrf.request', id=wo.ID))
    return render_template("cmrf/make_report.html", form=form, request=wo)

@cmrf.route('/report/<int:id>', methods=['GET'])
@login_required
def report(id):
    rp = Report.query.get_or_404(id)
    wo = WorkOrder.query.filter_by(RPT_ID=rp.ID).first_or_404()
    if current_user.id != wo.RSC_ID:
        if not current_user.can(Permission.ALL_R):
            abort(404)
    return render_template("cmrf/report.html", report=rp)



