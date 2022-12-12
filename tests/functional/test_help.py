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


def test_edithelp_not_loggedin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/edithelp' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(url_for('admin.edithelp'), follow_redirects=True)
    assert 'Zapisz kolejność' not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_edithelp_not_admin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/edithelp' page is requested (GET) by non-admin user
    THEN index page is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['admin'] = False
    response = client.get(url_for('admin.edithelp'), follow_redirects=True)
    assert 'Zapisz kolejność' not in response.data.decode('utf-8')
    assert 'testuser' in response.data.decode('utf-8')


def test_edithelp_admin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/edithelp' page is requested (GET) by admin user
    THEN edit help items page is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.get(url_for('admin.edithelp'), follow_redirects=True)
    assert 'Zapisz kolejność' in response.data.decode('utf-8')
    assert 'testadmin' in response.data.decode('utf-8')


def test_edithelp_add_item(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/helpedit' page is requested (POST) by admin user
            adding help item
    THEN new help item is visible
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.edithelp'), data={
            'helpitemtitle': 'Tytuł 6',
            'helpitembody': 'Treść 6'
            }, follow_redirects=True)
    assert 'Tytuł 6' in response.data.decode('utf-8')
    assert 'Treść 6' in response.data.decode('utf-8')
