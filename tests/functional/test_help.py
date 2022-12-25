from flask import url_for


def test_help_nologin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/help' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(
            url_for('basic.help'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Tytuł 1' not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_help_user(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/help' page is requested (GET) by user
    THEN help page is displayed
    """
    response = user_client.get(
            url_for('basic.help'),
            headers={'accept-language': 'pl'}
            )
    assert 'Tytuł 1' in response.data.decode('utf-8')


def test_help_admin(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/help' page is requested (GET) by admin user
    THEN help page with admin section is displayed
    """
    response = admin_client.get(
            url_for('basic.help'),
            headers={'accept-language': 'pl'}
            )
    assert 'Tytuł admin 1' in response.data.decode('utf-8')


def test_edit_help_not_loggedin(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/edit_help' page is requested (GET) by anonymous client
    THEN login page is displayed
    """
    response = client.get(
            url_for('admin.edit_help'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Zapisz kolejność' not in response.data.decode('utf-8')
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_edit_help_not_admin(user_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/edit_help' page is requested (GET) by non-admin user
    THEN index page is displayed
    """
    response = user_client.get(
            url_for('admin.edit_help'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Zapisz kolejność' not in response.data.decode('utf-8')
    assert 'testuser' in response.data.decode('utf-8')


def test_edit_help_admin(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/edit_help' page is requested (GET) by admin user
    THEN edit help items page is displayed
    """
    response = admin_client.get(
            url_for('admin.edit_help'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert 'Zapisz kolejność' in response.data.decode('utf-8')
    assert 'testadmin' in response.data.decode('utf-8')


def test_edit_help_add_item(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/helpedit' page is requested (POST) by admin user
            adding help item
    THEN new help item is visible
    """
    response = admin_client.post(url_for('admin.edit_help'), data={
            'helpitemtitle': 'Tytuł 6',
            'helpitembody': 'Treść 6'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Tytuł 6' in response.data.decode('utf-8')
    assert 'Treść 6' in response.data.decode('utf-8')


def test_edit_help_delete_item(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/helpedit' page is requested (POST) by admin user
            deleting help item
    THEN help item is not visible
    """
    response = admin_client.post(url_for('admin.edit_help'), data={
            'del_helpitem': 'submit',
            'helpitem_id': 1
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Tytuł 1' not in response.data.decode('utf-8')
    assert 'Treść 1' not in response.data.decode('utf-8')


def test_edit_help_change_item(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/helpedit' page is requested (POST) by admin user
            changing help item
    THEN help item has new value
    """
    response = admin_client.post(url_for('admin.edit_help'), data={
            'save_helpitem': 'submit',
            'helpitem_id': 1,
            'title': 'Tytuł zmieniony',
            'body': 'Treść zmieniona'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert 'Tytuł 1' not in response.data.decode('utf-8')
    assert 'Treść 1' not in response.data.decode('utf-8')
    assert 'Tytuł zmieniony' in response.data.decode('utf-8')
    assert 'Treść zmieniona' in response.data.decode('utf-8')


def test_edit_help_reorder_items(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/helpedit' page is requested (POST) by admin user
            changing help items order
    THEN help items are displayed in new order
    """
    response = admin_client.post(url_for('admin.edit_help'), data={
            'userhelp_order': '2,3,4,5,1',
            'adminhelp_order': '6,7,8'
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert response.data.decode('utf-8').index('Tytuł 2') \
        < response.data.decode('utf-8').index('Tytuł 1')
