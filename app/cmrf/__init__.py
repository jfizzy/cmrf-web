from flask import Blueprint

cmrf = Blueprint('cmrf', __name__)

from . import views
