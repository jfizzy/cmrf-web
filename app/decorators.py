from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

def make_r_required(f):
    return permission_required(Permission.MAKE_R)(f)

def view_r_required(f):
    return permission_required(Permission.VIEW_R)(f)

def add_article_required(f):
    return permission_required(Permission.ADD_ARTICLE)(f)

def all_r_required(f):
    return permission_required(Permission.ALL_R)(f)

def editing_required(f):
    return permission_required(Permission.EDITING)(f)

def user_acc_required(f):
    return permission_required(Permission.USER_ACC)(f)

