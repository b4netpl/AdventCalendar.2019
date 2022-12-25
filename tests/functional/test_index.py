from flask import url_for


def test_index_nologin(client):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that response is valid
    """
    response = client.get(
            url_for('basic.index'),
            follow_redirects=True,
            headers={'accept-language': 'pl'}
            )
    assert response.request.path == '/login'
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_login(client):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/login' page is requested (POST)
    THEN login page is displayed
    """
    response = client.get(
            url_for('basic.login'),
            headers={'accept-language': 'pl'}
            )
    assert response.status_code == 200
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_index_quest_answer_wrong(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (POST) with wrong answer to quest
    THEN error message is given and link to quest is still visible
    """
    with admin_client.session_transaction() as sess:
        sess['time_shift'] = 17
    response = admin_client.post(url_for('basic.index'), data={
            "day_id": 1,
            "answer": "pięć"
            }, headers={'accept-language': 'pl'})
    assert 'To nie jest prawidłowa odpowiedź...' \
        in response.data.decode('utf-8')
    assert 'data-bs-target="#discoverpopup1">17</a>' \
        in response.data.decode('utf-8')


def test_index_quest_answer_correct(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (POST) with correct answer to quest
    THEN quest is solved and link to quest is missing
    """
    with admin_client.session_transaction() as sess:
        sess['time_shift'] = 17
    response = admin_client.post(url_for('basic.index'), data={
            "day_id": 1,
            "answer": "cztery"
            }, headers={'accept-language': 'pl'})
    assert 'data-bs-target="#discoverpopup1">17</a>' \
        not in response.data.decode('utf-8')


def test_index_no_quest_for_day(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (POST) with a day without quest
    THEN quest is solved and link to quest is missing
    """
    with admin_client.session_transaction() as sess:
        sess['time_shift'] = 17
    response = admin_client.post(url_for('basic.index'), data={
            "day_id": 2
            }, headers={'accept-language': 'pl'})
    assert 'data-bs-target="#discoverpopup1">2</a>' \
        not in response.data.decode('utf-8')


def test_index_win(admin_client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (GET) with all quests solved
    THEN index page with congratulations is displayed
    """
    response = admin_client.post(url_for('admin.tweaks'), data={
            'solve_users': [2]
            }, follow_redirects=True, headers={'accept-language': 'pl'})
    assert '<h1 class="display-5 fw-bold">' \
        in response.data.decode('utf-8')
