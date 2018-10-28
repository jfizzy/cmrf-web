import os
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func
from ..decorators import admin_required, all_r_required, view_r_required, make_r_required, user_acc_required, \
	add_article_required, editing_required
from ..models import WorkOrder, User, Permission, Report, NewsItem, Publication, Person
from . import cmrf
from .. import db, documents, photos
from .forms import RequestForm, ReportForm, NewsItemForm, PublicationForm, PublicationEditForm, PersonForm, \
	PersonEditForm


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
	return render_template('cmrf/adm_requests.html', requests=requests, selected_id=id)


@cmrf.route('/request/<int:id>', methods=['GET'])
@login_required
@view_r_required
def view_request(id):
	request = WorkOrder.query.filter_by(ID=str(id)).first_or_404()

	if current_user.id != request.RSC_ID:
		if not current_user.can(Permission.ALL_R):
			abort(404)
	user = User.query.filter_by(UCID=request.RSC_ID).first()
	return render_template('cmrf/request.html', request=request, owner=user)


@cmrf.route('/delete-request/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_request(id):
	wo = WorkOrder.query.get_or_404(id)
	rp = Report.query.filter_by(ID=wo.RPT_ID).first()
	if rp is not None:
		db.session.delete(rp)
	db.session.delete(wo)
	db.session.commit()
	flash('Request Deleted as well as any Associated Reports.')
	return redirect(url_for('cmrf.all_requests'))


@cmrf.route('/make-request', methods=['GET', 'POST'])
@login_required
@make_r_required
def make_request():
	form = RequestForm(request.form)
	if form.validate_on_submit():
		wo = WorkOrder(title=form.title.data,
					   no_samples=form.no_samples.data,
					   RSC_ID=current_user.UCID,
					   desc=form.desc.data,
					   tm=form.tm.data,
					   ri=form.ri.data,
					   assistance=form.assistance.data)
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
	wo.ADM_ID = current_user.UCID  # for records
	db.session.add(wo)
	db.session.commit()
	flash('Request Approved.')
	return redirect(url_for('cmrf.view_request', id=wo.ID))


@cmrf.route('/cancel-request/<int:id>', methods=['GET'])
@login_required
@all_r_required
def cancel_request(id):
	wo = WorkOrder.query.get_or_404(id)
	wo.status = 'Cancelled'
	wo.ADM_ID = current_user.UCID  # for records
	db.session.add(wo)
	db.session.commit()
	flash('Request Cancelled.')
	return redirect(url_for('cmrf.view_request', id=wo.ID))


@cmrf.route('/edit-request/<int:id>', methods=['GET', 'POST'])
@login_required
@user_acc_required
def edit_request(id):
	wo = WorkOrder.query.get_or_404(id)
	woid = wo.ID
	form = RequestForm(request.form, wo=wo)
	if form.validate_on_submit():
		wo.title = form.title.data
		wo.no_samples = form.no_samples.data
		wo.desc = form.desc.data
		wo.tm = form.desc.data
		wo.assistance = bool(form.assistance.data)
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
	form.assistance.data = wo.assistance
	return render_template("cmrf/edit_request.html", id=wo.RSC_ID, form=form, woid=woid)


@cmrf.route('/all-requests')
@login_required
@all_r_required
def all_requests():
	requests = WorkOrder.query.join(User,
									WorkOrder.RSC_ID == User.UCID).add_columns(
		WorkOrder.ID, WorkOrder.RSC_ID, User.first_name,
		User.last_name, WorkOrder.title, WorkOrder.submit_date,
		WorkOrder.no_samples, WorkOrder.status).order_by(
		WorkOrder.submit_date.desc()).all()
	return render_template('cmrf/all_requests.html',
						   title=None, requests=requests)


@cmrf.route('/all-active-requests')
@login_required
@all_r_required
def all_active_requests():
	requests = WorkOrder.query.filter_by(status='In Progress').join(User,
																	WorkOrder.RSC_ID == User.UCID).add_columns(
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
																		 WorkOrder.RSC_ID == User.UCID).add_columns(
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
																 WorkOrder.RSC_ID == User.UCID).add_columns(
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
	requests = WorkOrder.query.filter_by(status='Cancelled').join(User,
																  WorkOrder.RSC_ID == User.UCID).add_columns(
		WorkOrder.ID, WorkOrder.RSC_ID, User.first_name,
		User.last_name, WorkOrder.title, WorkOrder.submit_date,
		WorkOrder.no_samples, WorkOrder.status).order_by(WorkOrder.submit_date.desc())
	return render_template('cmrf/all_requests.html',
						   title='Cancelled', requests=requests)


@cmrf.route('/make-report/<int:id>', methods=['GET', 'POST'])
@login_required
@all_r_required
def make_report(id):
	wo = WorkOrder.query.get_or_404(id)
	form = ReportForm(request.form)
	if form.validate_on_submit():
		report = Report(float(form.balance.data.replace(', ', '')), wo.ID, desc=form.desc.data,
						file_loc=form.file_loc.data)
		db.session.add(report)
		db.session.commit()
		wo.RPT_ID = report.ID
		wo.status = 'Complete'
		db.session.add(wo)
		db.session.commit()
		flash('Report Submitted Successfully')
		return redirect(url_for('cmrf.report', id=report.ID))
	return render_template("cmrf/make_report.html", form=form, request=wo)


@cmrf.route('/report/<int:id>', methods=['GET'])
@login_required
def report(id):
	rp = Report.query.get_or_404(id)
	wo = WorkOrder.query.filter_by(RPT_ID=rp.ID).first_or_404()
	if current_user.id != wo.RSC_ID:
		if not current_user.can(Permission.ALL_R):
			abort(404)
	return render_template("cmrf/report.html", report=rp, wo=wo)


@cmrf.route('/edit-report/<int:id>', methods=['GET', 'POST'])
@login_required
@all_r_required
def edit_report(id):
	rp = Report.query.get_or_404(id)
	wo = WorkOrder.query.filter_by(RPT_ID=rp.ID).first_or_404()
	form = ReportForm(request.form, rp=rp)
	if form.validate_on_submit():
		rp.balance = float(form.balance.data.replace(', ', ''))
		rp.desc = form.desc.data
		rp.file_loc = form.file_loc.data
		db.session.add(rp)
		db.session.commit()
		flash('Changes Saved Successfully')
		return redirect(url_for('cmrf.report', id=rp.ID))
	form.balance.data = rp.balance
	form.desc.data = rp.desc
	form.file_loc.data = rp.file_loc
	return render_template("cmrf/edit_report.html", errors=form.errors.items(), rp=rp, wo=wo, form=form)


@cmrf.route('/delete-report/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_report(id):
	rp = Report.query.get_or_404(id)
	wo = WorkOrder.query.filter_by(RPT_ID=rp.ID).first()
	wo.RPT_ID = None
	wo.status = 'In Progress'
	db.session.add(wo)
	db.session.delete(rp)
	db.session.commit()
	flash('Report Deleted')
	return redirect(url_for('cmrf.all_requests'))


@cmrf.route('/add-news-item', methods=['GET', 'POST'])
@login_required
@add_article_required
def add_news_item():
	form = NewsItemForm(request.form)
	if form.validate_on_submit():
		if request.files['file']:
			filename = photos.save(request.files['file'])
			url = photos.url(filename)
			news = NewsItem(current_user.id, title=form.title.data, desc=form.desc.data, url=form.url.data,
							image=filename)
		else:
			news = NewsItem(current_user.id, title=form.title.data, desc=form.desc.data, url=form.url.data, image=None)
		db.session.add(news)
		db.session.commit()
		flash('News Item Added Successfully')
		return redirect(url_for('main.news'))
	return render_template("cmrf/add_news_item.html", errors=form.errors.items(), form=form)


@cmrf.route('/edit-news-item/<int:id>', methods=['GET', 'POST'])
@login_required
@editing_required
def edit_news_item(id):
	ni = NewsItem.query.get_or_404(id)
	form = NewsItemForm(request.form, ni=ni)
	if form.validate_on_submit():
		if request.files['file']:
			if ni.image is not None and os.path.isfile(os.path.join('./app/uploads/photos/' + ni.image)):
				os.remove(os.path.join('./app/uploads/photos/' + ni.image))
			filename = photos.save(request.files['file'])
			url = photos.url(filename)
			ni.image = filename
		ni.title = form.title.data
		ni.desc = form.desc.data
		ni.url = form.url.data
		db.session.add(ni)
		db.session.commit()
		flash('Changes Saved Successfully')
		return redirect(url_for('main.news'))
	form.title.data = ni.title
	form.desc.data = ni.desc
	form.url.data = ni.url
	return render_template("cmrf/edit_news_item.html", errors=form.errors.items(), form=form, ni=ni)


@cmrf.route('/delete-news-item/<int:id>', methods=['GET'])
@login_required
@editing_required
def delete_news_item(id):
	ni = NewsItem.query.get_or_404(id)
	if ni.image is not None and os.path.isfile(os.path.join('./app/uploads/photos/' + ni.image)):
		os.remove(os.path.join('./app/uploads/photos/' + ni.image))
	db.session.delete(ni)
	db.session.commit()
	flash('News Item Deleted.')
	return redirect(url_for('cmrf.all_news_items'))


@cmrf.route('/all-news-items', methods=['GET'])
@login_required
@editing_required
def all_news_items():
	newsitems = NewsItem.query.join(User, NewsItem.UCID == User.UCID).all()
	return render_template("cmrf/all_news_items.html", newsitems=newsitems)


# Publication management routes

@cmrf.route('/add-publication', methods=['GET', 'POST'])
@login_required
@add_article_required
def add_publication():
	form = PublicationForm()
	if form.validate_on_submit():
		filename = documents.save(request.files['file'])
		url = documents.url(filename)
		publication = Publication(current_user.id, form.title.data, form.desc.data, filename, url)
		db.session.add(publication)
		db.session.commit()
		flash('Publication Added Successfully')
		return redirect(url_for('main.publications'))
	return render_template("cmrf/add_publication.html", errors=form.errors.items(), form=form)


@cmrf.route('/edit-publication/<int:id>', methods=['GET', 'POST'])
@login_required
@editing_required
def edit_publication(id):
	p = Publication.query.get_or_404(id)
	form = PublicationEditForm(request.form, p=p)
	if form.validate_on_submit():
		if request.files['file']:
			os.remove(os.path.join('./app/uploads/documents/' + p.pdf_name))
			filename = documents.save(request.files['file'])
			url = documents.url(filename)
			p.pdf_name = filename
			p.pdf_url = url
		p.title = form.title.data
		p.desc = form.desc.data
		db.session.add(p)
		db.session.commit()
		flash('Changes Saved Successfully')
		return redirect(url_for('main.publications'))
	form.title.data = p.title
	form.desc.data = p.desc
	return render_template("cmrf/edit_publication.html", errors=form.errors.items(), form=form, p=p)


@cmrf.route('/delete-publication/<int:id>', methods=['POST'])
@login_required
@editing_required
def delete_publication(id):
	p = Publication.query.get_or_404(id)
	os.remove(os.path.join('./app/uploads/documents/' + p.pdf_name))
	db.session.delete(p)
	db.session.commit()
	flash('Publication Successfully removed')
	return redirect(url_for('main.publications'))


@cmrf.route('/manage-publications', methods=['GET'])
@login_required
@editing_required
def manage_publications():
	pubs = Publication.query.order_by(Publication.submit_date.desc()).all()
	return render_template("cmrf/manage_publications.html", pubs=pubs)


# Person management routes

@cmrf.route('/add-person', methods=['GET', 'POST'])
@login_required
@editing_required
def add_person():
	form = PersonForm(request.form)
	if form.validate_on_submit():
		if request.files['file']:
			filename = photos.save(request.files['file'])
			url = photos.url(filename)
		else:
			filename = None
			url = None
		person = Person(current_user.id, form.name.data, form.title.data, form.caption.data, form.email.data, filename,
						url)
		db.session.add(person)
		db.session.commit()
		flash('Person Added Successfully')
		return redirect(url_for('main.team'))
	return render_template("cmrf/add_person.html", errors=form.errors.items(), form=form)


@cmrf.route('/edit-person/<int:id>', methods=['GET', 'POST'])
@login_required
@editing_required
def edit_person(id):
	per = Person.query.get_or_404(id)
	form = PersonEditForm(request.form, per=per)
	if form.validate_on_submit():
		if request.files['file']:
			if per.photo_name is not None and os.path.isfile(os.path.join('./app/uploads/photos/' + per.photo_name)):
				os.remove(os.path.join('./app/uploads/photos/' + per.photo_name))
			per.photo_name = photos.save(request.files['file'])
			per.photo_url = photos.url(per.photo_name)
		per.name = form.name.data
		per.title = form.title.data
		per.caption = form.caption.data
		per.email = form.email.data
		if per.alumni != form.alumni.data:
			per.alumni = form.alumni.data
			per.position = 1
		db.session.add(per)
		db.session.commit()
		flash('Person Updated Successfully')
		return redirect(url_for('cmrf.manage_people'))
	form.name.data = per.name
	form.title.data = per.title
	form.caption.data = per.caption
	form.email.data = per.email
	form.alumni.data = per.alumni
	return render_template("cmrf/edit_person.html", errors=form.errors.items(), form=form, per=per)


@cmrf.route('/person-up/<int:id>', methods=['GET'])
@login_required
@editing_required
def person_up(id):
	per = Person.query.get_or_404(id)
	qry = db.session.query(func.max(Person.position).label("max_pos"))
	max_pos = qry.one()
	if per.position <= max_pos:
		per.position = per.position + 1
		db.session.add(per)
		db.session.commit()
		flash('Person moved up in section of page')
	return redirect(url_for('cmrf.manage_people'))


@cmrf.route('/person-down/<int:id>', methods=['GET'])
@login_required
@editing_required
def person_down(id):
	per = Person.query.get_or_404(id)
	qry = db.session.query(func.min(Person.position).label("min_pos"))
	min_pos = qry.one()
	if per.position > 0:
		per.position = per.position - 1
		db.session.add(per)
		db.session.commit()
		flash('Person moved down in section of page')
	return redirect(url_for('cmrf.manage_people'))


@cmrf.route('/delete-person/<int:id>', methods=['GET', 'POST'])
@login_required
@editing_required
def delete_person(id):
	per = Person.query.get_or_404(id)
	if per.photo_name is not None and os.path.isfile(os.path.join('./app/uploads/photos/' + per.photo_name)):
		os.remove(os.path.join('./app/uploads/photos/' + per.photo_name))
	db.session.delete(per)
	db.session.commit()
	flash('Person Successfully removed')
	return redirect(url_for('main.team'))


@cmrf.route('/manage-people', methods=['GET'])
@login_required
@editing_required
def manage_people():
	ppl = Person.query.filter(Person.alumni.is_(False)).order_by(Person.submit_date.desc()).all()
	alum = Person.query.filter(Person.alumni.is_(True)).order_by(Person.submit_date.desc()).all()
	return render_template("cmrf/manage_people.html", ppl=ppl, alum=alum)
