from advencal import db
from flask import current_app


def commit(dbsession):
    try:
        dbsession.commit()
    except db.exc.DBAPIError as ex:
        current_app.logger.error(ex.orig)
        dbsession.rollback()
