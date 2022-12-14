import pytest

from datetime import time
from advencal import create_app, db, init_db_cli
from advencal.models import User, Day, Help


@pytest.fixture
def flask_app():
    flask_app = create_app('config.TestConfig')

    yield flask_app


@pytest.fixture
def client(flask_app):

    app_context = flask_app.test_request_context()
    app_context.push()

    return flask_app.test_client()


@pytest.fixture
def runner_client(flask_app):

    init_db_cli.register(flask_app)

    # app_context = flask_app.test_request_context()
    app_context = flask_app.app_context()
    app_context.push()

    return flask_app.test_cli_runner()


@pytest.fixture
def init_database(client):
    db.create_all()

    user1 = User(id=1, username='testuser', admin=False)
    user1.set_password('user')
    user2 = User(id=2, username='testadmin', admin=True)
    user2.set_password('admin')
    db.session.add(user1)
    db.session.add(user2)

    default_hour = time(hour=0, minute=0, second=0)

    db.session.add(Day(
            id=1,
            day_no=17,
            quest='Ile to dwa razy dwa',
            quest_answer='cztery',
            hour=default_hour
            ))
    db.session.add(Day(id=2, day_no=2, hour=default_hour))
    db.session.add(Day(id=3, day_no=15, hour=default_hour))
    db.session.add(Day(id=4, day_no=8, hour=default_hour))
    db.session.add(Day(id=5, day_no=24, hour=default_hour))
    db.session.add(Day(id=6, day_no=9, hour=default_hour))
    db.session.add(Day(id=7, day_no=19, hour=default_hour))
    db.session.add(Day(id=8, day_no=6, hour=default_hour))
    db.session.add(Day(id=9, day_no=11, hour=default_hour))
    db.session.add(Day(id=10, day_no=22, hour=default_hour))
    db.session.add(Day(id=11, day_no=4, hour=default_hour))
    db.session.add(Day(id=12, day_no=14, hour=default_hour))
    db.session.add(Day(id=13, day_no=18, hour=default_hour))
    db.session.add(Day(id=14, day_no=5, hour=default_hour))
    db.session.add(Day(id=15, day_no=21, hour=default_hour))
    db.session.add(Day(id=16, day_no=7, hour=default_hour))
    db.session.add(Day(id=17, day_no=20, hour=default_hour))
    db.session.add(Day(id=18, day_no=13, hour=default_hour))
    db.session.add(Day(id=19, day_no=10, hour=default_hour))
    db.session.add(Day(id=20, day_no=1, hour=default_hour))
    db.session.add(Day(id=21, day_no=23, hour=default_hour))
    db.session.add(Day(id=22, day_no=16, hour=default_hour))
    db.session.add(Day(id=23, day_no=3, hour=default_hour))
    db.session.add(Day(id=24, day_no=12, hour=default_hour))

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


@pytest.fixture
def new_user():
    user = User(id=1, username='test', admin=False)
    user.set_password('user')
    return user


@pytest.fixture
def new_admin():
    user = User(id=2, username='testadmin', admin=True)
    user.set_password('admin')
    return user


@pytest.fixture
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


@pytest.fixture
def new_helpitem():
    helpitem = Help(
            id=1,
            order=1,
            title='Tytuł',
            body='Treść',
            admin=False
            )
    return helpitem
