from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException
from pglast import parse_sql, parse_plpgsql

from app.auth import Auth
from app.config import Settings
from app.main import app
from app.security import COOKIE_NAME, SUPABASE_COOKIE, REFRESH_COOKIE


def test_confirmation_does_not_set_session(client, headers):
    app.state.auth.confirmation_required = True
    response = client.post('/api/auth/register', headers=headers, json={
        'email': 'verify@example.com', 'password': 'correct-pass123', 'name': '인증 대기'})
    assert response.status_code == 201
    assert response.json()['confirmation_required'] is True
    assert COOKIE_NAME not in client.cookies
    assert client.get('/api/me').status_code == 401


def test_supabase_identity_required_even_with_valid_shop_cookie(client, signed_in):
    app.state.auth.sessions.clear()
    assert client.get('/api/me').status_code == 401


def test_refresh_rotates_cookies_and_preserves_identity(client, headers, signed_in):
    old_refresh = client.cookies[REFRESH_COOKIE]
    app.state.auth.sessions.clear()
    assert client.get('/api/me').status_code == 401
    response = client.post('/api/auth/refresh', headers=headers)
    assert response.status_code == 200
    assert client.cookies[REFRESH_COOKIE] != old_refresh
    assert client.get('/api/me').json()['id'] == signed_in['id']
    assert 'access_token' not in response.text


def test_protected_page_refreshes_expired_access(client, signed_in):
    app.state.auth.sessions.clear()
    assert client.get('/account').status_code == 200
    assert client.get('/api/me').status_code == 200


def test_full_cookie_replay_after_logout_is_blocked(client, headers, signed_in):
    cookies = dict(client.cookies)
    assert client.post('/api/auth/logout', headers=headers).status_code == 200
    client.cookies.clear()
    client.cookies.update(cookies)
    assert client.get('/api/me').status_code == 401
    assert client.post('/api/auth/refresh', headers=headers).status_code == 401


def test_password_change_revokes_full_previous_session(client, headers, signed_in):
    old = dict(client.cookies)
    response = client.patch('/api/me', headers=headers, json={'name': '새 이름',
        'current_password': 'correct-pass123', 'new_password': 'changed-pass123'})
    assert response.status_code == 200
    client.cookies.clear()
    client.cookies.update(old)
    assert client.get('/api/me').status_code == 401
    assert client.post('/api/auth/refresh', headers=headers).status_code == 401


def test_refresh_requires_csrf_and_bound_cookie(client, headers, signed_in):
    assert client.post('/api/auth/refresh').status_code == 403
    client.cookies.set(REFRESH_COOKIE, 'tampered', domain='testserver.local', path='/')
    assert client.post('/api/auth/refresh', headers=headers).status_code == 401


def test_blocked_account_cannot_refresh_or_login(client, headers, signed_in, db):
    db.users[0]['is_active'] = False
    assert client.get('/api/me').status_code == 401
    assert client.post('/api/auth/refresh', headers=headers).status_code == 401
    assert client.post('/api/auth/login', headers=headers, json={
        'email': signed_in['email'], 'password': 'correct-pass123'}).status_code == 401


def test_admin_permissions_and_live_role_revocation(client, headers, signed_in, db):
    assert client.get('/admin').status_code == 403
    assert client.get('/api/admin/orders').status_code == 403
    product = {'name': '관리 상품', 'description': '설명', 'category': '리빙', 'price': 1000, 'stock': 5}
    assert client.post('/api/admin/products', headers=headers, json=product).status_code == 403
    assert client.put('/api/admin/products/'+str(uuid4()), headers=headers, json=product).status_code == 403
    db.users[0]['role'] = 'admin'
    assert client.get('/admin').status_code == 200
    assert client.get('/api/admin/orders').status_code == 200
    db.users[0]['role'] = 'member'
    assert client.get('/api/admin/orders').status_code == 403


def test_cannot_assign_role_or_identity_through_profile(client, headers, signed_in):
    for field in ('role', 'auth_user_id', 'is_active', 'token_version', 'email'):
        assert client.patch('/api/me', headers=headers, json={'name': '공격', field: 'admin'}).status_code == 422
    assert client.post('/api/auth/register', headers=headers, json={
        'name': '공격', 'email': 'attack@example.com', 'password': 'correct-pass123', 'role': 'admin'}).status_code == 422


def test_admin_product_writes_target_only_requested_product(client, headers, signed_in, db, monkeypatch):
    db.users[0]['role'] = 'admin'
    product_id = str(uuid4())
    product = {'name': '관리 상품', 'description': '설명', 'category': '리빙',
               'price': 1000, 'stock': 5, 'image_key': 'mug', 'is_active': False}
    calls = []
    def request(method, table, **kwargs):
        calls.append((method, table, kwargs))
        return [{'id': product_id, **kwargs['data']}]
    monkeypatch.setattr(db, 'request', request)
    assert client.post('/api/admin/products', headers=headers, json=product).status_code == 201
    assert calls[-1] == ('POST', 'products', {'data': product})
    assert client.put('/api/admin/products/'+product_id, headers=headers, json=product).status_code == 200
    assert calls[-1] == ('PATCH', 'products', {'params': {'id': 'eq.'+product_id}, 'data': product})
    assert client.put('/api/admin/products/'+product_id, headers=headers,
                      json={**product, 'role': 'admin'}).status_code == 422


def test_admin_update_missing_product_returns_404(client, headers, signed_in, db, monkeypatch):
    db.users[0]['role'] = 'admin'
    monkeypatch.setattr(db, 'request', lambda *args, **kwargs: [])
    assert client.put('/api/admin/products/'+str(uuid4()), headers=headers, json={
        'name': '없는 상품', 'description': '설명', 'category': '리빙', 'price': 1000, 'stock': 0}).status_code == 404


def test_all_session_cookies_are_private_and_cleared(client, headers, signed_in):
    response = client.post('/api/auth/login', headers=headers,
        json={'email': signed_in['email'], 'password': 'correct-pass123'})
    cookies = response.headers.get_list('set-cookie')
    for name in (COOKIE_NAME, SUPABASE_COOKIE, REFRESH_COOKIE):
        cookie = next(c for c in cookies if c.startswith(name+'='))
        assert 'HttpOnly' in cookie and 'SameSite=lax' in cookie
    assert client.post('/api/auth/logout', headers=headers).status_code == 200
    assert not any(name in client.cookies for name in (COOKIE_NAME, SUPABASE_COOKIE, REFRESH_COOKIE))


def test_auth_delete_failure_still_blocks_shop_access(client, headers, signed_in, monkeypatch):
    def fail(identity):
        raise HTTPException(503, 'offline')
    monkeypatch.setattr(app.state.auth, 'delete_user', fail)
    assert client.request('DELETE', '/api/me', headers=headers, json={'password': 'correct-pass123'}).status_code == 503
    assert client.get('/api/me').status_code == 401
    assert client.post('/api/auth/refresh', headers=headers).status_code == 401


@pytest.mark.parametrize('key', ['sb_secret_test', 'legacy-service-role'])
def test_auth_transport_uses_request_scoped_tokens(key):
    auth = Auth(Settings(supabase_url='https://example.supabase.co', supabase_key=key, jwt_secret='x'*48))
    auth.client.close()
    seen = []
    def handle(request):
        seen.append(request)
        assert request.headers['apikey'] == key
        return httpx.Response(200, json={'id': 'user'})
    auth.client = httpx.Client(base_url='https://example.supabase.co/auth/v1/',
        headers={'apikey': key}, transport=httpx.MockTransport(handle))
    auth.login('member@example.com', 'secret')
    auth.user('user-a')
    auth.user('user-b')
    auth.refresh('refresh-a')
    auth.logout('user-a')
    auth.password('user-b', 'new-secret')
    auth.delete_user('identity-a')
    assert seen[0].url.params['grant_type'] == 'password'
    assert 'authorization' not in seen[0].headers
    assert seen[1].headers['authorization'] == 'Bearer user-a'
    assert seen[2].headers['authorization'] == 'Bearer user-b'
    assert 'authorization' not in seen[3].headers
    assert seen[3].url.params['grant_type'] == 'refresh_token'
    assert seen[4].url.params['scope'] == 'global'
    assert seen[5].method == 'PUT'
    assert seen[6].method == 'DELETE'
    assert ('authorization' in seen[6].headers) == (not key.startswith('sb_secret_'))
    auth.close()


@pytest.mark.parametrize('status,expected', [(400,401),(401,401),(429,429),(500,503)])
def test_auth_errors_are_redacted(status, expected):
    auth = Auth(Settings(supabase_url='https://example.supabase.co', supabase_key='test', jwt_secret='x'*48))
    auth.client.close()
    auth.client = httpx.Client(base_url='https://example.supabase.co/auth/v1/',
        transport=httpx.MockTransport(lambda r: httpx.Response(status, json={'message': 'private-secret'})))
    with pytest.raises(HTTPException) as error:
        auth.user('private-token')
    assert error.value.status_code == expected
    assert 'private' not in error.value.detail
    auth.close()


def test_auth_migration_sql_syntax():
    sql = (Path(__file__).resolve().parents[1]/'sql/004_supabase_auth.sql').read_text(encoding='utf-8')
    assert parse_sql(sql)
    for marker in ('create or replace function public.shop_auth_profile()', 'create or replace function public.shop_mutate'):
        function = marker + sql.split(marker,1)[1].split('$$;',1)[0] + '$$;'
        assert parse_plpgsql(function)
