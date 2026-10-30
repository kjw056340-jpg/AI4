from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException
from pglast import parse_sql, parse_plpgsql

from app.config import Settings
from app.db import Database
from app.security import COOKIE_NAME, safe_next
from tests.conftest import PRODUCT_ID


def test_public_products_and_pages(client):
    assert client.get('/api/products').json()['items'][0]['price'] == 18000
    assert client.get('/api/products/' + PRODUCT_ID).status_code == 200
    response = client.get('/product?id=' + PRODUCT_ID)
    assert response.status_code == 200
    assert 'name="viewport"' in response.text
    assert 'script-src \'self\'' in response.headers['content-security-policy']
    assert client.get('/static/js/app.js').status_code == 200
    assert client.get('/static/images/mug.svg').status_code == 200


@pytest.mark.parametrize('path', ['/cart', '/account', '/orders', '/checkout?source=direct&product_id=' + PRODUCT_ID])
def test_protected_screen_preserves_next(client, path):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 303
    from urllib.parse import parse_qs, urlsplit
    assert parse_qs(urlsplit(response.headers['location']).query)['next'][0] == path


@pytest.mark.parametrize('path', ['/api/cart', '/api/me', '/api/orders', '/api/payments/' + str(uuid4())])
def test_private_api_without_login(client, path):
    assert client.get(path).status_code == 401


def test_csrf_on_registration_and_foreign_origin(client, headers):
    body = {'email': 'test@example.com', 'password': 'correct-pass123', 'name': '이름'}
    assert client.post('/api/auth/register', json=body).status_code == 403
    assert client.post('/api/auth/register', headers={**headers, 'Origin': 'https://evil.example'}, json=body).status_code == 403
    assert client.post('/api/auth/register', headers={**headers, 'Sec-Fetch-Site': 'cross-site'}, json=body).status_code == 403


@pytest.mark.parametrize('configured,secure,origin,expected', [
    ('http://127.0.0.1:8000', False, 'http://localhost:8000', 401),
    ('http://localhost:8000', False, 'http://127.0.0.1:8000', 401),
    ('http://127.0.0.1:8000', False, 'http://localhost:9000', 403),
    ('http://127.0.0.1:8000', False, 'https://localhost:8000', 403),
    ('https://shop.example.com', True, 'http://localhost:8000', 403),
    ('https://shop.example.com', True, 'https://shop.example.com', 401),
    ('http://127.0.0.1:8000', True, 'http://localhost:8000', 403),
])
def test_csrf_local_alias_and_production_boundary(client, headers, monkeypatch, configured, secure, origin, expected):
    settings = Settings(supabase_url='https://example.supabase.co', supabase_key='test',
                        jwt_secret='test-secret-' * 4, app_origin=configured, cookie_secure=secure)
    monkeypatch.setattr('app.main.get_settings', lambda: settings)
    response = client.post('/api/auth/login', headers={**headers, 'Origin': origin},
                           json={'email': 'missing@example.com', 'password': 'incorrect123'})
    assert response.status_code == expected


def test_csrf_local_alias_still_requires_token(client, headers, monkeypatch):
    settings = Settings(supabase_url='https://example.supabase.co', supabase_key='test',
                        jwt_secret='test-secret-' * 4, app_origin='http://127.0.0.1:8000', cookie_secure=False)
    monkeypatch.setattr('app.main.get_settings', lambda: settings)
    response = client.post('/api/auth/login', headers={'Origin': 'http://localhost:8000'},
                           json={'email': 'missing@example.com', 'password': 'incorrect123'})
    assert response.status_code == 403


def test_signup_auth_cookie_and_duplicate(client, headers, signed_in, db):
    assert 'password_hash' not in db.users[0]
    assert 'password' not in db.users[0]
    assert db.users[0]['auth_user_id']
    assert 'password_hash' not in client.get('/api/me').text
    response = client.post('/api/auth/login', headers=headers, json={'email': 'MEMBER@example.com','password': 'correct-pass123'})
    cookie = response.headers['set-cookie'].lower()
    assert 'httponly' in cookie and 'samesite=lax' in cookie
    assert client.post('/api/auth/register', headers=headers, json={'email':'member@example.com','password':'correct-pass123','name':'다른 이름'}).status_code == 400


def test_login_next_logout_revocation(client, headers, signed_in):
    target = '/checkout?source=direct&product_id=' + PRODUCT_ID + '&quantity=2'
    response = client.post('/api/auth/login', params={'next':target}, headers=headers, json={'email':'member@example.com','password':'correct-pass123'})
    assert response.json()['next'] == target
    old_cookie = client.cookies[COOKIE_NAME]
    assert client.post('/api/auth/logout', headers=headers).status_code == 200
    client.cookies.set(COOKIE_NAME, old_cookie)
    assert client.get('/api/me').status_code == 401
    assert client.get('/account', follow_redirects=False).status_code == 303


@pytest.mark.parametrize('target', ['https://evil.example', '//evil.example','/%2f%2fevil.example', '/\\evil.example', '/login', '/api/me', '/products%0aevil'])
def test_open_redirect_blocked(target):
    assert safe_next(target) == '/products'


def test_wrong_password_and_generic_login_error(client, headers, signed_in):
    for email in ['member@example.com', 'missing@example.com']:
        response=client.post('/api/auth/login',headers=headers,json={'email':email,'password':'wrong12345'})
        assert response.status_code == 401
        assert response.json()['detail'] == '이메일 또는 비밀번호를 확인하거나 다시 로그인해 주세요.'


def test_password_change_revokes_old_token(client, headers, signed_in):
    old = client.cookies[COOKIE_NAME]
    response=client.patch('/api/me',headers=headers,json={'name':'새 이름','phone':'010-9999-0000','address':'서울시 새주소 123',
        'current_password':'correct-pass123','new_password':'changed-pass123'})
    assert response.status_code == 200
    assert client.get('/api/me').json()['name'] == '새 이름'
    client.cookies.set(COOKIE_NAME, old)
    assert client.get('/api/me').status_code == 401


def test_delete_requires_password_and_revokes(client,headers,signed_in):
    assert client.request('DELETE','/api/me',headers=headers,json={'password':'wrong'}).status_code == 401
    old=client.cookies[COOKIE_NAME]
    assert client.request('DELETE','/api/me',headers=headers,json={'password':'correct-pass123'}).status_code == 200
    client.cookies.set(COOKIE_NAME,old)
    assert client.get('/api/me').status_code == 401


def test_ownership_filters_on_orders_and_payment(client, signed_in, db):
    assert client.get('/api/orders/' + str(uuid4())).status_code == 404
    assert db.calls[-1][2]['user_id'] == 'eq.' + signed_in['id']
    assert client.get('/api/payments/' + str(uuid4())).status_code == 404
    assert db.calls[-1][2]['user_id'] == 'eq.' + signed_in['id']


def test_mutation_identity_not_from_request(client,headers,signed_in,db):
    data={'product_id':PRODUCT_ID,'quantity':2}
    assert client.post('/api/cart/items',headers=headers,json={**data,'user_id':str(uuid4())}).status_code == 422
    assert client.post('/api/cart/items',headers=headers,json=data).status_code == 200
    assert db.calls[-1] == ('mutate','cart_add',data)
    assert client.post('/api/payments',headers=headers,json={'order_id':str(uuid4()),'idempotency_key':str(uuid4()),'amount':1}).status_code == 422


@pytest.mark.parametrize('quantity', [0,-1,100,1.5,'2',True])
def test_invalid_quantity(client,headers,signed_in,quantity):
    assert client.post('/api/cart/items',headers=headers,json={'product_id':PRODUCT_ID,'quantity':quantity}).status_code == 422


def test_password_policy_and_redacted_errors(client,headers):
    secret='한'*30+'123'
    response=client.post('/api/auth/register',headers=headers,json={'email':'test@example.com','password':secret,'name':'이름'})
    assert response.status_code == 422
    assert secret not in response.text


def test_rate_limit(client,headers):
    from app.main import limiter
    for _ in range(15): limiter.allow('testclient')
    response=client.post('/api/auth/login',headers=headers,json={'email':'none@example.com','password':'nope'})
    assert response.status_code == 429 and response.headers['retry-after']=='60'


def test_database_transport_new_and_legacy_keys():
    for key in ['sb_secret_test', 'legacy-test-key']:
        db=Database(Settings(supabase_url='https://example.supabase.co',supabase_key=key,jwt_secret='x'*48))
        def handle(request):
            assert request.headers['apikey']==key
            assert ('authorization' in request.headers) == (not key.startswith('sb_secret_'))
            assert request.url.params['email']=='eq.x+y@example.com'
            return httpx.Response(200,json=[])
        db.client.close()
        db.client=httpx.Client(base_url='https://example.supabase.co/rest/v1/',headers={
            'apikey':key,**({'Authorization':'Bearer '+key} if not key.startswith('sb_secret_') else {})},transport=httpx.MockTransport(handle))
        assert db.select('users',email='eq.x+y@example.com')==[]
        db.close()


def test_database_error_mapping():
    db=Database(Settings(supabase_url='https://example.supabase.co',supabase_key='test',jwt_secret='x'*48))
    db.client.close()
    db.client=httpx.Client(base_url='https://example.supabase.co/rest/v1/',transport=httpx.MockTransport(
        lambda request: httpx.Response(400,json={'message':'OUT_OF_STOCK','code':'P0001'})))
    with pytest.raises(HTTPException) as error: db.mutate({'id':str(uuid4()),'token_version':0},'pay')
    assert error.value.status_code==409
    db.close()


def test_postgresql_and_plpgsql_syntax():
    root=Path(__file__).resolve().parent.parent
    sql=(root/'sql/001_schema.sql').read_text(encoding='utf-8')
    assert parse_sql(sql)
    function='create function public.shop_mutate'+sql.split('create function public.shop_mutate',1)[1].split('revoke all on function',1)[0]
    assert parse_plpgsql(function)
    assert parse_sql((root/'sql/002_seed.sql').read_text(encoding='utf-8'))
