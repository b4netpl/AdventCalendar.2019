from flask import url_for


def test_changepass_nologin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/changepass' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(url_for('basic.changepass'), follow_redirects=True)
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_changepass_wrong_password(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/changepass' page is requested (POST) with incorrect password
    THEN error message is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    response = client.post(url_for('basic.changepass'), data={
            "old_pass": "incorrect",
            "new_pass": "whatever",
            "new_pass_again": "whatever"
            })
    assert 'Niepoprawne hasło' in response.data.decode('utf-8')


def test_changepass_new_password_not_identical(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/changepass' page is requested (POST) with new password not
            identical with repeated new password
    THEN error message is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    response = client.post(url_for('basic.changepass'), data={
            "old_pass": "user",
            "new_pass": "whatever",
            "new_pass_again": "incorrect"
            })
    assert 'Nowe hasła nie są jednakowe' in response.data.decode('utf-8')


def test_changepass_correct(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/changepass' page is requested (POST) with correct data
    THEN confirmation message is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    response = client.post(url_for('basic.changepass'), data={
            "old_pass": "user",
            "new_pass": "whatever",
            "new_pass_again": "whatever"
            }, follow_redirects=True)
    assert 'Hasło zmienione poprawnie' in response.data.decode('utf-8')
