from flask import render_template, session, redirect, url_for, current_app, abort
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm
from pathlib import Path
import os


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/index')
@main.route('/home')
def home():
    return redirect('/')

@main.route('/people')
def people():
    posts = [
        {
            'pic': '../static/assets/IMG_4804.JPG',
            'name': 'Dr. Ian Lewis',
            'title': 'Principal Investigator',
            'caption': 'Assistant Professor, AIHS Chair in Translational Health - Metabolomics. Dr.Lewis identifies and develops research objectives.',
            'dept': 'BIO-442, Department of Biological Sciences',
            'school': 'University of Calgary',
            'address': '2500 University Drive NW',
            'city': 'Calgary, Alberta, Canada',
            'postal': 'T2N 1N4',
            'tel': '+1 (403) 220-4366',
            'email': 'Dr. Ian Lewis',
            'emailaddress': 'ian.lewis2@ucalgary.ca'
        },
        {
            'pic': '../static/assets/Andrew_S.jpg',
            'name': 'Dr. Andrew Stopford',
            'title': 'Staff',
            'caption': 'Facility Director/Instrumentation Specialist',
            'dept': 'BIO-442, Department of Biological Sciences',
            'school': 'University of Calgary',
            'address': '2500 University Drive NW',
            'city': 'Calgary, Alberta, Canada',
            'postal': 'T2N 1N4',
            'tel': '+1 (403) 220-6242',
            'fax': '+1 (403) 210-9460',
            'email': 'Dr. Andrew Stopford',
            'emailaddress': 'andrew.stopford@ucalgary.ca',
            'email2': 'CMRF',
            'emailaddress2': 'omics@ucalgary.ca'
        },
        {
            'pic': '../static/assets/IMG_4807.JPG',
            'name': 'Dr. Vishaldeep Sidhu',
            'title': 'Staff',
            'caption': 'Lewis Research Group Laboratory Manager. Responsible for all aspects of the lab, including equipment, software, and documentation.',
            'dept': 'BIO-442, Department of Biological Sciences',
            'school': 'University of Calgary',
            'address': '2500 University Drive NW',
            'city': 'Calgary, Alberta, Canada',
            'postal': 'T2N 1N4',
            'tel': '+1 (403) 220-4849',
            'fax': '+1 (403) 210-9460',
            'email': 'Dr. Vishaldeep Sidhu',
            'emailaddress': 'vishaldeep.sidhu@ucalgary.ca'
        },
        {
            'pic': '../static/assets/IMG_5194.JPG',
            'name': 'Ryan Groves',
            'title': 'Staff',
            'caption': 'As a scientific labratory staff member, Ryanin is involved in a variety of labratory-based-investigations.'
        },
        {
            'pic': '../static/assets/Matthias_K.jpg',
            'name': 'Dr. Matthias Klein',
            'title': 'Graduate Student',
            'caption': 'Performs a variety of administrative tasks including preparation of Power Point presentation, data entry and analysis.'
        },
        {
            'pic': '../static/assets/IMG_4806.JPG',
            'name': 'Travis Bingeman',
            'title': 'Graduate Student',
            'caption': 'Facility Director/Instrumentation Specialist. Facilitates projects in an office with other students.'
        },
        {
            'pic': '../static/assets/IMG_4811.JPG',
            'name': 'Michelle Chang',
            'title': 'Graduate Student',
            'caption': 'Provides assistance with event planning including supervision of undergraduate student workers.'
        },
        {
            'pic': '../static/assets/Hassan_H.jpg',
            'name': 'Hassan Hazari',
            'title': 'Graduate Student',
            'caption': 'Responsible for configuration and managment of instruments in the lab used for metabolic research testing.'
        },
        {
            'pic': '../static/assets/Kurt_E.jpg',
            'name': 'Kurt Ebeling',
            'title': 'Undergraduate Student',
            'caption': 'Preforms routine tasks in the research lab, without constant supervision.'
        },
        {
            'pic': '../static/assets/placeholder.png',
            'name': 'Austin Nguyen',
            'title': 'Undergraduate Student',
            'caption': 'Say something, I\'m giving up on you.'
        },
        {
            'pic': '../static/assets/placeholder.png',
            'name': 'Selena Osman',
            'title': 'Undergraduate Student',
            'caption': 'Say something, I\'m giving up on you.'
        }
    ]
    return render_template("people.html", posts=posts)

@main.route('/instruments')
@main.route('/inst')
def inst():
    return render_template('inst.html')

@main.route('/research')
def research():
    return render_template('research.html')

@main.route('/view-image/<image>')
def view_image(image):
    # print(os.getcwd())
    # image_file = Path("/static/assets/placeholder.png")
    # print(image_file)
    # if image_file.is_file():
    return render_template('view_image.html', image=image)
    # else:
    #     return abort(404)
