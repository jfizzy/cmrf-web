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

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/instruments')
@main.route('/inst')
def inst():
    return render_template('inst.html')

@main.route('/news')
def news():
    return render_template('news.html')
