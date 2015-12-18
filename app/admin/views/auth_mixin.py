from functools import wraps

from flask import current_app, url_for, flash, session
from flask_login import current_user
from werkzeug.utils import redirect


def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.is_admin:
            session['_flashes'] = []
            flash('Only admins can access this page', 'error')
            return redirect(url_for('logout'))
        return func(*args, **kwargs)
    return decorated_view

