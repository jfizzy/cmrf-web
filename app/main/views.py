from flask import render_template, session, redirect, url_for, current_app, abort
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm
from pathlib import Path


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
            'caption': 'Assistant Professor, AIHS Chair in Translational Health - Metabolomics. Let us fill this space, naw mean?',
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
            'pic': '../static/assets/placeholder.png',
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
            'caption': 'Lewis Research Group Laboratory Manager. It would be cool if we could get more info maybe?',
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
            'caption': 'Awaiting Description. For now I\'ll just say he\'s a swell guy!'
        },
        {
            'pic': '../static/assets/placeholder.png',
            'name': 'Dr. Matthias Klein',
            'title': 'Graduate Student',
            'caption': 'Facility Director/Instrumentation Specialist'
        },
        {
            'pic': '../static/assets/IMG_4806.JPG',
            'name': 'Travis Bingeman',
            'title': 'Graduate Student',
            'caption': 'Awaiting Description. For now I\'ll just say he\'s a swell guy!'
        },
        {
            'pic': '../static/assets/IMG_4811.JPG',
            'name': 'Michelle Chang',
            'title': 'Graduate Student',
            'caption': 'Say something, I\'m giving up on you.'
        },
        {
            'pic': '../static/assets/placeholder.png',
            'name': 'Hassan Hazari',
            'title': 'Graduate Student',
            'caption': 'Say something, I\'m giving up on you.'
        },
        {
            'pic': '../static/assets/placeholder.png',
            'name': 'Kurt Ebeling',
            'title': 'Undergraduate Student',
            'caption': 'Say something, I\'m giving up on you.'
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
    posts = [
    {
        'pic': '../static/assets/inst_eg1.jpg',
        'desc': 'This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer'
    },
    {
        'pic': '../static/assets/inst_eg2.jpg',
        'desc': 'This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer'
    },
    {
        'pic': '../static/assets/inst_eg3.jpg',
        'desc': 'This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer'
    },
    {
        'pic': '../static/assets/inst_eg4.jpg',
        'desc': 'This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer'
    }
    ]
    return render_template('inst.html', posts=posts)

@main.route('/research')
def research():
    return render_template('research.html')

@main.route('/view-image/<image>')
def view_image(image):
    image_file = Path("static/assets/" + image)
    if image_file.is_file():
        render_template('view_image.html', image=image)
    else:
        abort(404)
