from flask import url_for


def test_users_not_loggedin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(url_for('admin.users'), follow_redirects=True)
    assert 'Dodaj użytkownika' not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_users_not_admin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (GET) by non-admin user
    THEN index page is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['admin'] = False
    response = client.get(url_for('admin.users'), follow_redirects=True)
    assert 'Dodaj użytkownika' not in response.data.decode('utf-8')
    assert 'testuser' in response.data.decode('utf-8')


def test_users_admin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (GET) by admin user
    THEN users page is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.get(url_for('admin.users'), follow_redirects=True)
    assert 'Dodaj użytkownika' in response.data.decode('utf-8')
    assert 'testadmin' in response.data.decode('utf-8')


def test_users_add_user_exists(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            adding user with user name that already exists
    THEN error message is displayed
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.users'), data={
            'new_user': 'testuser'
            }, follow_redirects=True)
    assert 'Użytkownik <strong>testuser</strong> już istnieje' \
        in response.data.decode('utf-8')


def test_users_add_user_given_password(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            adding user with user name and typed in password
    THEN user is visible in users table and credentials are
            displayed (YES, THIS IS INTENTIONAL!)
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.users'), data={
            'new_user': 'testuser2',
            'pass_source': 'pass_input',
            'new_pass': 'passfromform'
            }, follow_redirects=True)
    assert 'testuser2' in response.data.decode('utf-8')
    assert 'passfromform' in response.data.decode('utf-8')


def test_users_add_user_random_password(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            adding user with user name and random password
    THEN user is visible in users table but typed in password is not used
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.users'), data={
            'new_user': 'testuser2',
            'pass_source': 'pass_gen',
            'new_pass': 'passfromform'
            }, follow_redirects=True)
    assert 'testuser2' in response.data.decode('utf-8')
    assert 'passfromform' not in response.data.decode('utf-8')


def test_users_change_user_password_given(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            changing user's password with typed in password
    THEN changed credentials are displayed (YES, THIS IS INTENTIONAL!)
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.users'), data={
            'user_id': 1,
            'change_pass_source': 'change_pass_input',
            'change_pass': 'passfromform'
            }, follow_redirects=True)
    assert 'testuser' in response.data.decode('utf-8')
    assert 'passfromform' in response.data.decode('utf-8')


def test_users_change_user_password_random(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            changing user's password with random password
    THEN changed credentials are displayed (YES, THIS IS INTENTIONAL!)
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.users'), data={
            'user_id': 1,
            'change_pass_source': 'change_pass_gen',
            'change_pass': 'passfromform'
            }, follow_redirects=True)
    assert 'testuser' in response.data.decode('utf-8')
    assert 'passfromform' not in response.data.decode('utf-8')


def test_users_del_user(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            deleting user
    THEN message is displayed and then user is not visible in the users table
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['admin'] = True
    response = client.post(url_for('admin.users'), data={
            'user_del': 1
            }, follow_redirects=True)
    assert 'Użytkownik <strong>testuser</strong> został usunięty' \
        in response.data.decode('utf-8')
    response = client.get(url_for('admin.users'), follow_redirects=True)
    assert 'testuser' not in response.data.decode('utf-8')
