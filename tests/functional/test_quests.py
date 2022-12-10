import io

from flask import url_for


def test_quest_edit_not_loggedin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(url_for('admin.questsed'), follow_redirects=True)
    assert 'Edytuj questy' not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_quest_edit_not_admin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (GET) by non-admin user
    THEN index page is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['admin'] = False
    response = client.get(url_for('admin.questsed'), follow_redirects=True)
    assert 'Edytuj questy' not in response.data.decode('utf-8')
    assert 'testuser' in response.data.decode('utf-8')


def test_quest_edit_admin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (GET) by non-admin user
    THEN index page is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.get(url_for('admin.questsed'), follow_redirects=True)
    assert 'Edytuj questy' in response.data.decode('utf-8')
    assert 'testadmin' in response.data.decode('utf-8')


def test_quest_del_quest(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (POST) with quest_del param
    THEN the requested quest is not visible in list
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.questsed'), data={
            "quest_del": 1
            }, follow_redirects=True)
    assert 'Edytuj questy' in response.data.decode('utf-8')
    assert 'Ile to dwa razy dwa' not in response.data.decode('utf-8')


def test_quest_upload_asset(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/questsed' page is requested (POST) with upload_asset param
    THEN file is uploaded to assets
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    # fs.create_file('./advencal/static/quests/meh.jpg')
    response = client.post(url_for('admin.questsed'), data={
            "upload_asset": (io.BytesIO(b":|"), 'meh.jpg')
            }, follow_redirects=True, content_type='multipart/form-data')
    with open('./advencal/static/quests/meh.jpg') as f:
        asset = f.read()
        assert ':|' in asset
    assert 'meh.jpg' in response.data.decode('utf-8')
