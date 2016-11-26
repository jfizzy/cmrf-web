from flask import render_template, redirect, request, url_for, flash
from . import cmrf

@cmrf.route('/', methods=['GET'])
def index():
    return render_template('cmrf/cmrf.html')
