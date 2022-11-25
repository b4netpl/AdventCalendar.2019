from advencal import app, db


def commit(dbsession):
    try:
        dbsession.commit()
    except db.exc.DBAPIError as ex:
        app.logger.error(ex.orig)
        dbsession.rollback()
