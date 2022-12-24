from flask import url_for, session


def test_login_user_incorrect(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/login' page is requested (POST) with incorrect credentials
    THEN check that error message is given and login page is displayed
    """
    response = client.post(url_for('basic.login'), data={
            "username": "incorrectuser",
            "password": "user"
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert response.status_code == 200
    assert 'Zmień hasło' not in response.data.decode('utf-8')
    assert 'Niepoprawny login' in response.data.decode('utf-8')

    response = client.post(url_for('basic.login'), data={
            "username": "testuser",
            "password": "incorrectpass"
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert response.status_code == 200
    assert 'Zmień hasło' not in response.data.decode('utf-8')
    assert 'Niepoprawne hasło' in response.data.decode('utf-8')


def test_login_user_correct(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/login' page is requested (POST) with correct credentials
    THEN user is logged in and index page is displayed
    """
    response = client.post(url_for('basic.login'), data={
            "username": "testuser",
            "password": "user"
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert response.status_code == 200
    assert 'Zmień hasło' in response.data.decode('utf-8')


def test_logout(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN user is logged out (no session) and login page is displayed
    """
    response = user_client.get(
            url_for('basic.logout'),
            headers={'accept-language': 'pl'}
            )
    assert session.get('user_id') is None
    assert 'Zmień hasło' not in response.data.decode('utf-8')


def test_login_loggedin_user(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/login' page is requested (GET) by logged in user
    THEN index page is displayed
    """
    response = user_client.get(
            url_for('basic.login'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert response.status_code == 200
    assert 'Zmień hasło' in response.data.decode('utf-8')
