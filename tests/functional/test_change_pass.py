from flask import url_for


def test_change_pass_nologin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/change_pass' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(
            url_for('basic.change_pass'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_change_pass_wrong_password(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/change_pass' page is requested (POST) with incorrect password
    THEN error message is displayed
    """
    response = user_client.post(url_for('basic.change_pass'), data={
            "old_pass": "incorrect",
            "new_pass": "whatever",
            "new_pass_again": "whatever"
            }, headers={'accept-language': 'pl'})
    assert 'Niepoprawne hasło' in response.data.decode('utf-8')


def test_change_pass_new_password_not_identical(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/change_pass' page is requested (POST) with new password not
            identical with repeated new password
    THEN error message is displayed
    """
    response = user_client.post(url_for('basic.change_pass'), data={
            "old_pass": "user",
            "new_pass": "whatever",
            "new_pass_again": "incorrect"
            }, headers={'accept-language': 'pl'})
    assert 'Nowe hasła nie są jednakowe' in response.data.decode('utf-8')


def test_chang_epass_correct(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/change_pass' page is requested (POST) with correct data
    THEN confirmation message is displayed
    """
    response = user_client.post(url_for('basic.change_pass'), data={
            "old_pass": "user",
            "new_pass": "whatever",
            "new_pass_again": "whatever"
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Hasło zmienione poprawnie' in response.data.decode('utf-8')
