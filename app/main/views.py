from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm


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
            'header': 'Dr. Ian Lewis',
            'caption': 'Description goes here. Get info from lewisresearchgroup.org. PLACEHOLDER TEXT. PLACEHOLDER TEXT. PLACEHOLDER TEXT.'
        },
        {
            'pic': '../static/assets/IMG_4806.JPG',
            'header': 'Person 2',
            'caption': 'Description goes here. Get info from lewisresearchgroup.org. PLACEHOLDER TEXT. PLACEHOLDER TEXT. PLACEHOLDER TEXT.'
        },
        {
            'pic': '../static/assets/IMG_4807.JPG',
            'header': 'Person 3',
            'caption': 'Description goes here. Get info from lewisresearchgroup.org. PLACEHOLDER TEXT. PLACEHOLDER TEXT. PLACEHOLDER TEXT.'
        },
        {
            'pic': '../static/assets/IMG_4811.JPG',
            'header': 'Person 4',
            'caption': 'Description goes here. Get info from lewisresearchgroup.org. PLACEHOLDER TEXT. PLACEHOLDER TEXT. PLACEHOLDER TEXT.'
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
