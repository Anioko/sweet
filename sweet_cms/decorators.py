from functools import wraps

from flask import flash, abort, redirect, url_for, request
from flask_login import current_user

from sweet_cms.applications.api.views import main_api


def admin_required(f):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('admin.login'))
            elif not current_user.is_admin:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator(f)


def anonymous_required(f):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                if current_user.is_admin and 'admin' in request.endpoint:
                    return redirect(url_for('admin.index'))
                else:
                    return redirect(url_for('public.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator(f)


def api_route(route, route_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            main_api.add_resource(f, route, endpoint=route_name)
        decorated_function()
    return decorator
