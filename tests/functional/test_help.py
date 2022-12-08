from flask import url_for


def test_help_nologin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/help' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(url_for('basic.help'), follow_redirects=True)
    assert 'Tytuł 1' not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_help_user(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/help' page is requested (GET) by user
    THEN help page is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    response = client.get(url_for('basic.help'))
    assert 'Tytuł 1' in response.data.decode('utf-8')


def test_help_admin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/help' page is requested (GET) by admin user
    THEN help page with admin section is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['admin'] = True
    response = client.get(url_for('basic.help'))
    assert 'Tytuł admin 1' in response.data.decode('utf-8')
