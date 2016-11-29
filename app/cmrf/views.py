from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required
from . import cmrf

@cmrf.route('/', methods=['GET'])
@login_required
def index():
    return render_template('cmrf/cmrf.html')
