"""Tests for authentication views."""


def test_login_page_loads(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert 'ログイン' in resp.data.decode('utf-8')


def test_login_invalid_credentials(client, test_user):
    resp = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert 'パスワードが正しくありません' in resp.data.decode('utf-8')


def test_login_success(client, test_user):
    resp = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123',
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_logout_redirects_to_login(client, test_user):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass123'})
    resp = client.get('/logout', follow_redirects=True)
    assert resp.status_code == 200
    assert 'ログイン' in resp.data.decode('utf-8')


def test_protected_route_redirects(client):
    resp = client.get('/salary/', follow_redirects=False)
    assert resp.status_code in (302, 401)
