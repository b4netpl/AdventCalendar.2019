import io
import os

from flask import url_for


def test_quests_edit_not_loggedin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(
            url_for('admin.questsed'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Edytuj questy' not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_quests_edit_not_admin(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (GET) by non-admin user
    THEN index page is displayed
    """
    response = user_client.get(
            url_for('admin.questsed'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Edytuj questy' not in response.data.decode('utf-8')
    assert 'testuser' in response.data.decode('utf-8')


def test_quests_edit_admin(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (GET) by admin user
    THEN quests edit page is displayed
    """
    response = admin_client.get(
            url_for('admin.questsed'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Edytuj questy' in response.data.decode('utf-8')
    assert 'testadmin' in response.data.decode('utf-8')


def test_quests_del_quest(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (POST) with quest_del param
    THEN the requested quest is not visible in list
    """
    response = admin_client.post(url_for('admin.questsed'), data={
            "quest_del": 1
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Edytuj questy' in response.data.decode('utf-8')
    assert 'Ile to dwa razy dwa' not in response.data.decode('utf-8')


def test_fake_fs(admin_client, init_database, fs):
    """
    This is to avoid a strange bug. First use of pyfakefs fixture in tests
    will always make first request redirected to login page, even though
    flask-login test client is used.
    """
    fs.add_real_directory(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            os.pardir,
            'advencal',
            'templates'
            ))
    fs.add_real_directory(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            os.pardir,
            'venv',
            'lib',
            'python3.9',
            'site-packages',
            'babel'
            ))
    response = admin_client.post(url_for('admin.questsed'), data={
            "asset_del": "meh.jpg"
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_quests_del_asset(admin_client, init_database, fs):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (POST) with asset_del param
    THEN file is deleted from assets
    """
    fs.add_real_directory(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            os.pardir,
            'advencal',
            'templates'
            ))
    fs.add_real_directory(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            os.pardir,
            'venv',
            'lib',
            'python3.9',
            'site-packages',
            'babel'
            ))
    fs.create_file('./advencal/static/quests/meh.jpg', contents=':|')
    response = admin_client.post(url_for('admin.questsed'), data={
            "asset_del": "meh.jpg"
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Zaloguj' not in response.data.decode('utf-8')
    assert os.path.exists('./advencal/static/quests/meh.jpg') is False
    assert 'meh.jpg' not in response.data.decode('utf-8')


def test_quests_upload_asset(admin_client, init_database, fs):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (POST) with upload_asset param
    THEN file is uploaded to assets
    """
    fs.add_real_directory(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            os.pardir,
            'advencal',
            'templates'
            ))
    fs.add_real_directory(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            os.pardir,
            'venv',
            'lib',
            'python3.9',
            'site-packages',
            'babel'
            ))

    fs.create_file('./advencal/static/quests/meh.jpg')
    response = admin_client.post(
            url_for('admin.questsed'), data={
                "upload_asset": (io.BytesIO(b":|"), 'meh.jpg')
                },
            follow_redirects=True,
            content_type='multipart/form-data',
            headers={'accept-language': 'pl'}
            )
    with open('./advencal/static/quests/meh.jpg') as f:
        asset = f.read()
        assert ':|' in asset
    assert 'meh.jpg' in response.data.decode('utf-8')


def test_questedit_not_loggedin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questedit' page is requested (POST) by anonymous client
    THEN login page is displayed
    """
    response = client.post(url_for('admin.questedit'), data={
            'quest_edit': 1
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Edytuj treść questa i odpowiedź' \
        not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_questedit_not_admin(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questedit' page is requested (POST) by non-admin user
    THEN index page is displayed
    """
    response = user_client.post(url_for('admin.questedit'), data={
            'quest_edit': 1
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Edytuj treść questa i odpowiedź' \
        not in response.data.decode('utf-8')
    assert 'testuser' in response.data.decode('utf-8')


def test_questedit_admin(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questedit' page is requested (POST) by admin user
    THEN quest edit page is displayed
    """
    response = admin_client.post(url_for('admin.questedit'), data={
            'quest_edit': 1
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Edytuj treść questa i odpowiedź' in response.data.decode('utf-8')
    assert 'testadmin' in response.data.decode('utf-8')


def test_questedit_edit(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questedit' page is requested (POST) by admin user
            with new quest data
    THEN quest edit page is displayed with data changed
    """
    response = admin_client.post(url_for('admin.questedit'), data={
            'day_id': 2,
            'quest': 'Ile to dwa dodać trzy?',
            'quest_answer': 'pięć',
            'hour': '12:34:56'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Edytuj questy' in response.data.decode('utf-8')
    assert 'Ile to dwa dodać trzy?' in response.data.decode('utf-8')
    assert 'pięć' in response.data.decode('utf-8')
    assert '12:34:56' in response.data.decode('utf-8')
