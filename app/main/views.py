from flask import render_template, session, redirect, url_for, current_app, abort, make_response, send_from_directory
import os
from .. import db
from ..models import User, NewsItem, Publication, Person
from ..email import send_email
from . import main
from .forms import NameForm
from pathlib import Path
from flask_sqlalchemy import get_debug_queries


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/index')
@main.route('/home')
def home():
    return redirect('/')

@main.route('/team')
def team():
    people = Person.query.filter(Person.alumni.is_(False)).order_by(Person.position.desc()).all()
    alumni = Person.query.filter(Person.alumni.is_(True)).order_by(Person.position.desc()).all()
    return render_template("team.html", people=people, alumni=alumni)

@main.route('/facilities')
def facilities():
    return render_template('facilities.html')

@main.route('/location')
def location():
	return render_template('location.html')
	
@main.route('/news')
def news():
	newsitems = NewsItem.query.order_by(NewsItem.submit_date.desc()).all()
	
	return render_template('news.html', newsitems=newsitems)
	
@main.route('/research')
def research():
    return render_template('research.html')

@main.route('/analytics')
def analytics():
    return render_template('analytics.html')

@main.route('/malaria')
def malaria():
    return render_template('malaria.html')

@main.route('/hainfections')
def hainfections():
    return render_template('hainfections.html')

@main.route('/publications')
def publications():
	publications = Publication.query.order_by(Publication.submit_date.desc()).all()
	
	return render_template('publications.html', publications=publications)
	
@main.route('/publication/<int:id>')
def show_pub(id):
	doc = Publication.query.filter_by(ID=str(id)).first_or_404()
	#get binary document data
	with open('./app/uploads/documents/' + doc.pdf_name, mode='rb') as pdf:
		pdf_content = pdf.read()
		response = make_response(pdf_content)
		response.headers['Content-Type'] = 'application/pdf'
		response.headers['Content-Disposition'] = 'inline; filename=%s' % doc.pdf_name
		return response

@main.route('/photo/<int:id>')
def show_pic(id):
	person = Person.query.filter_by(ID=str(id)).first_or_404()
	with open('./app/uploads/photos/' + person.photo_name, mode='rb') as pic:
		pic_content = pic.read()
		response = make_response(pic_content)
		response.headers['Content-Type'] = 'image/%s' % person.photo_name.split('.')[1]
		response.headers['Content-Disposition'] = 'inline; filename=%s' % person.photo_name
		return response

@main.route('/thumb/<int:id>')
def show_thumb(id):
	ni = NewsItem.query.filter_by(ID=str(id)).first_or_404()
	with open('./app/uploads/photos/' + ni.image, mode='rb') as pic:
		pic_content = pic.read()
		response = make_response(pic_content)
		response.headers['Content-Type'] = 'image/%s' % ni.image.split('.')[1]
		response.headers['Content-Disposition'] = 'inline; filename=%s' % ni.image
		return response

@main.route('/assets/<path:path>')
def send_asset(path):
	try:
		with open('./app/static/assets/' + str(path), mode='rb') as asset:
			asset_content = asset.read()
			response = make_response(asset_content)
			response.headers['Content-Type'] = 'image/%s' % str(path).split('.')[1]
			response.headers['Content-Disposition'] = 'inline; filename=%s' % str(path)
			return response
	except:
		return abort(404)


@main.route('/view-image/<image>')
def view_image(image):
    return render_template('view_image.html', image=image)

@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['CMRF_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
                                       (query.statement, query.parameters, query.duration, query.context))
    return response
