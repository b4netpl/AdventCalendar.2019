from flask import url_for
from datetime import datetime


def test_tweaks_not_loggedin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/tweaks' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(
            url_for('admin.tweaks'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Postępy użytkowników' not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_tweaks_not_admin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/tweaks' page is requested (GET) by non-admin user
    THEN index page is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['admin'] = False
    response = client.get(
            url_for('admin.tweaks'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Postępy użytkowników' not in response.data.decode('utf-8')
    assert 'testuser' in response.data.decode('utf-8')


def test_tweaks_admin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/tweaks' page is requested (GET) by admin user
    THEN tweaks page is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.get(
            url_for('admin.tweaks'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Postępy użytkowników' in response.data.decode('utf-8')
    assert 'testadmin' in response.data.decode('utf-8')


def test_tweaks_solve(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/tweaks' page is requested (POST) by admin user
            with list of users to solve all quests
    THEN tweaks page is displayed with quests solved for these users
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.tweaks'), data={
            'solve_users': [1, 2]
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    response = client.get(
            url_for('admin.tweaks'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Postępy użytkowników' in response.data.decode('utf-8')
    assert 'background-color: yellow; color: green;' \
        in response.data.decode('utf-8')


def test_tweaks_del_visits(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/tweaks' page is requested (POST) by admin user
            with list of users to delete visits
    THEN index page is displayed with quests unsolved for these users
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.tweaks'), data={
            'solve_users': [2]
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    response = client.post(url_for('admin.tweaks'), data={
            'del_users': [2],
            'del_discos': 'del_taf',
            'del_except_quests': 'del_except_quests'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    response = client.get(
            url_for('admin.tweaks'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Postępy użytkowników' in response.data.decode('utf-8')
    assert 'border: 4px solid green;background-color: yellow; color: green' \
        in response.data.decode('utf-8')


def test_tweaks_timeshift(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/tweaks' page is requested (POST) by admin user
            with time shift value
    THEN index page is displayed for the day of time shift
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.tweaks'), data={
            'time_shift': 17
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Ile to dwa razy dwa' in response.data.decode('utf-8')
    assert '<a class="nav-link disabled">Dzień: 17</a>' \
        in response.data.decode('utf-8')


def test_tweaks_remove_timeshift(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/tweaks' page is requested (POST) by admin user
            with time shift value equal to present day
    THEN index page is displayed without time shift
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    date_today = datetime.today().day
    response = client.post(url_for('admin.tweaks'), data={
            'time_shift': date_today
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert '<a class="nav-link disabled">Dzień:' \
        not in response.data.decode('utf-8')
