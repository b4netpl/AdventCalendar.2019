from advencal import db
from flask import current_app, redirect, url_for
from flask_login import current_user
from functools import wraps


def commit(dbsession):
    try:
        dbsession.commit()
    except db.exc.DBAPIError as ex:
        current_app.logger.error(ex.orig)
        dbsession.rollback()


def admin_required(func):

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.admin:
            return redirect(url_for('basic.index'))
        return func(*args, **kwargs)

    return decorated_view
