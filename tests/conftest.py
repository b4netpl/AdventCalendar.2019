import pytest

from advencal import app
from advencal.models import User


@pytest.fixture(scope='module')
def flask_app():
    flask_app = app
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )

    yield flask_app


@pytest.fixture(scope='module')
def client(flask_app):
    return flask_app.test_client()


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
