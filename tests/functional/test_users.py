from flask import url_for


def test_users_not_loggedin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(
            url_for('admin.users'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Dodaj użytkownika' not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_users_not_admin(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (GET) by non-admin user
    THEN index page is displayed
    """
    response = user_client.get(
            url_for('admin.users'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Dodaj użytkownika' not in response.data.decode('utf-8')
    assert 'testuser' in response.data.decode('utf-8')


def test_users_admin(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (GET) by admin user
    THEN users page is displayed
    """
    response = admin_client.get(
            url_for('admin.users'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Dodaj użytkownika' in response.data.decode('utf-8')
    assert 'testadmin' in response.data.decode('utf-8')


def test_users_add_user_exists(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            adding user with user name that already exists
    THEN error message is displayed
    """
    response = admin_client.post(url_for('admin.users'), data={
            'new_user': 'testuser'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Użytkownik <strong>testuser</strong> już istnieje' \
        in response.data.decode('utf-8')


def test_users_add_user_given_password(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            adding user with user name and typed in password
    THEN user is visible in users table and credentials are
            displayed (YES, THIS IS INTENTIONAL!)
    """
    response = admin_client.post(url_for('admin.users'), data={
            'new_user': 'testuser2',
            'pass_source': 'pass_input',
            'new_pass': 'passfromform'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'testuser2' in response.data.decode('utf-8')
    assert 'passfromform' in response.data.decode('utf-8')


def test_users_add_user_random_password(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            adding user with user name and random password
    THEN user is visible in users table but typed in password is not used
    """
    response = admin_client.post(url_for('admin.users'), data={
            'new_user': 'testuser2',
            'pass_source': 'pass_gen',
            'new_pass': 'passfromform'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'testuser2' in response.data.decode('utf-8')
    assert 'passfromform' not in response.data.decode('utf-8')


def test_users_change_user_password_given(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            changing user's password with typed in password
    THEN changed credentials are displayed (YES, THIS IS INTENTIONAL!)
    """
    response = admin_client.post(url_for('admin.users'), data={
            'user_id': 1,
            'change_pass_source': 'change_pass_input',
            'change_pass': 'passfromform'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'testuser' in response.data.decode('utf-8')
    assert 'passfromform' in response.data.decode('utf-8')


def test_users_change_user_password_random(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            changing user's password with random password
    THEN changed credentials are displayed (YES, THIS IS INTENTIONAL!)
    """
    response = admin_client.post(url_for('admin.users'), data={
            'user_id': 1,
            'change_pass_source': 'change_pass_gen',
            'change_pass': 'passfromform'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'testuser' in response.data.decode('utf-8')
    assert 'passfromform' not in response.data.decode('utf-8')


def test_users_del_user(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/users' page is requested (POST) by admin user
            deleting user
    THEN message is displayed and then user is not visible in the users table
    """
    response = admin_client.post(url_for('admin.users'), data={
            'user_del': 1
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Użytkownik <strong>testuser</strong> został usunięty' \
        in response.data.decode('utf-8')
    response = admin_client.get(
            url_for('admin.users'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'testuser' not in response.data.decode('utf-8')
