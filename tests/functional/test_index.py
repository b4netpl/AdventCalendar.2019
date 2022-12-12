from flask import url_for


def test_index_nologin(client):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that response is valid
    """
    response = client.get(url_for('basic.index'), follow_redirects=True)
    assert response.request.path == '/login'
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_login(client):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (POST)
    THEN check that response is 405
    """
    response = client.get(url_for('basic.login'))
    assert response.status_code == 200
    assert 'Zaloguj' in response.data.decode('utf-8')


def test_index_quest_answer_wrong(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (POST) with wrong answer to quest
    THEN error message is given and link to quest is still visible
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['admin'] = True
        sess['time_shift'] = 17
    response = client.post(url_for('basic.index'), data={
            "day_id": 1,
            "answer": "pięć"
            })
    assert 'To nie jest prawidłowa odpowiedź...' \
        in response.data.decode('utf-8')
    assert 'data-bs-target="#discoverpopup1">17</a>' \
        in response.data.decode('utf-8')


def test_index_quest_answer_correct(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (POST) with correct answer to quest
    THEN quest is solved and link to quest is missing
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['admin'] = True
        sess['time_shift'] = 17
    response = client.post(url_for('basic.index'), data={
            "day_id": 1,
            "answer": "cztery"
            })
    assert 'data-bs-target="#discoverpopup1">17</a>' \
        not in response.data.decode('utf-8')


def test_index_no_quest_for_day(client, init_database):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (POST) with a day without quest
    THEN quest is solved and link to quest is missing
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['admin'] = True
        sess['time_shift'] = 17
    response = client.post(url_for('basic.index'), data={
            "day_id": 2
            })
    assert 'data-bs-target="#discoverpopup1">2</a>' \
        not in response.data.decode('utf-8')


# TODO test when win
