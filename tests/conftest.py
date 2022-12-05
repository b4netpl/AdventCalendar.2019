import pytest

from datetime import time
from advencal import create_app, db, init_db_cli
from advencal.models import User, Day, Help


@pytest.fixture(scope='module')
def flask_app():
    flask_app = create_app('config.TestConfig')

    yield flask_app


@pytest.fixture(scope='module')
def client(flask_app):

    app_context = flask_app.test_request_context()
    app_context.push()

    return flask_app.test_client()


@pytest.fixture(scope='module')
def runner_client(flask_app):

    init_db_cli.register(flask_app)

    # app_context = flask_app.test_request_context()
    app_context = flask_app.app_context()
    app_context.push()

    return flask_app.test_cli_runner()


@pytest.fixture(scope='module')
def init_database(client):
    db.create_all()

    user1 = User(id=1, username='testuser', admin=False)
    user1.set_password('user')
    user2 = User(id=2, username='testadmin', admin=True)
    user2.set_password('admin')
    db.session.add(user1)
    db.session.add(user2)

    default_hour = time(hour=0, minute=0, second=0)
    day = Day(
            id=1,
            day_no=5,
            quest='Ile to dwa razy dwa',
            quest_answer='cztery',
            hour=default_hour
            )
    db.session.add(day)

    help1 = Help(
        id=1,
        order=1,
        title='Tytuł 1',
        body='Treść 1',
        admin=False
        )
    help2 = Help(
        id=2,
        order=2,
        title='Tytuł 2',
        body='Treść 2',
        admin=False
        )
    help3 = Help(
        id=3,
        order=3,
        title='Tytuł 3',
        body='Treść 3',
        admin=False
        )
    help4 = Help(
        id=4,
        order=4,
        title='Tytuł 4',
        body='Treść 4',
        admin=False
        )
    help5 = Help(
        id=5,
        order=5,
        title='Tytuł 5',
        body='Treść 5',
        admin=False
        )
    help6 = Help(
        id=6,
        order=1,
        title='Tytuł admin 1',
        body='Treść admin 1',
        admin=True
        )
    help7 = Help(
        id=7,
        order=2,
        title='Tytuł admin 2',
        body='Treść admin 2',
        admin=True
        )
    help8 = Help(
        id=8,
        order=3,
        title='Tytuł admin 3',
        body='Treść admin 3',
        admin=True
        )
    db.session.add(help1)
    db.session.add(help2)
    db.session.add(help3)
    db.session.add(help4)
    db.session.add(help5)
    db.session.add(help6)
    db.session.add(help7)
    db.session.add(help8)

    db.session.commit()

    yield

    db.drop_all()


@pytest.fixture(scope='module')
def new_user():
    user = User(id=1, username='test', admin=False)
    user.set_password('user')
    return user


@pytest.fixture(scope='module')
def new_admin():
    user = User(id=2, username='testadmin', admin=True)
    user.set_password('admin')
    return user


@pytest.fixture(scope='module')
def new_day():
    default_hour = time(hour=0, minute=0, second=0)
    day = Day(
            id=1,
            day_no=5,
            quest='Ile to dwa razy dwa',
            quest_answer='cztery',
            hour=default_hour
            )
    return day


@pytest.fixture(scope='module')
def new_helpitem():
    helpitem = Help(
            id=1,
            order=1,
            title='Tytuł',
            body='Treść',
            admin=False
            )
    return helpitem
