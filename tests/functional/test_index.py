def test_index_nologin(client):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that response is valid
    """
    response = client.get('/', follow_redirects=True)
    assert response.request.path == '/login'
    assert b'2022 B4Team' in response.data


def test_login(client):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested (POST)
    THEN check that response is 405
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b'2022 B4Team' in response.data
