from flask import render_template, session, redirect, url_for, current_app, abort, make_response
import os
from .. import db
from ..models import User, NewsItem, Publication
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
    posts = [
        {
            'pic': '../static/assets/s_ian_lewis.jpg',
            'name': 'Dr. Ian Lewis',
            'title': 'Principal Investigator',
            'caption': 'AIHS Chair in Translational Health - Metabolomics, Assistant Professor',
            'dept': 'BIO-442, Department of Biological Sciences',
            'school': 'University of Calgary',
            'address': '2500 University Drive NW',
            'city': 'Calgary, Alberta, Canada',
            'postal': 'T2N 1N4',
            'tel': '+1 (403) 220-4366',
            'emailaddress': 'ian.lewis2@ucalgary.ca'
        },
        {
            'pic': '../static/assets/s_vishaldeep_sidhu.jpg',
            'name': 'Dr. Vishaldeep Sidhu',
            'title': 'Laboratory Manager',
            'caption': 'Lewis Research Group Laboratory Manager',
            'dept': 'BIO-497, Department of Biological Sciences',
            'school': 'University of Calgary',
            'address': '2500 University Drive NW',
            'city': 'Calgary, Alberta, Canada',
            'postal': 'T2N 1N4',
            'tel': '+1 (403) 220-4849',
            'emailaddress': 'vishaldeep.sidhu@ucalgary.ca'
        },
        {
            'pic': '../static/assets/s_ryan_groves.jpg',
            'name': 'Ryan Groves',
            'title': 'Staff'
        },
        {
            'pic': '../static/assets/placeholder.jpg',
            'name': 'Dr. Dominique Bihan',
            'title': 'Staff'
        },
        {
            'pic': '../static/assets/s_travis_bingeman.jpg',
            'name': 'Travis Bingeman',
            'title': 'Graduate Student',
            'caption': 'Facility Director/Instrumentation Specialist'
        },
        {
            'pic': '../static/assets/s_michelle_chang.jpg',
            'name': 'Michelle Chang',
            'title': 'Graduate Student',
            'caption': 'Provides assistance with event planning including supervision of undergraduate students'
        },
        {
            'pic': '../static/assets/placeholder.jpg',
            'name': 'Dr. Matthias Klein',
            'title': 'Graduate Student',
            'caption': 'Performs a variety of administrative tasks including data entry and analysis.'
        },
        {
            'pic': '../static/assets/placeholder.jpg',
            'name': 'Dr. Thomas Rydzak',
            'title': 'Graduate Student'
        },
        {
            'pic': '../static/assets/placeholder.jpg',
            'name': 'Austin Nguyen',
            'title': 'Graduate Student'
        }
    ]
    return render_template("team.html", posts=posts)

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
	
@main.route('/publication/<id>')
def show_pub(id):
	doc = Publication.query.filter_by(ID=str(id)).first_or_404()
	#get binary document data
	with open('./app/uploads/documents/' + doc.pdf_name, mode='rb') as pdf:
		pdf_content = pdf.read()
		response = make_response(pdf_content)
		response.headers['Content-Type'] = 'application/pdf'
		response.headers['Content-Disposition'] = 'inline; filename=%s' % doc.pdf_name
		return response

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
