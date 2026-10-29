import copy
import os
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

os.environ.setdefault('SUPABASE_URL', 'https://example.supabase.co')
os.environ.setdefault('SUPABASE_KEY', 'test-only-key')
os.environ.setdefault('JWT_SECRET', 'test-only-secret-' * 4)
os.environ.setdefault('APP_ORIGIN', 'http://testserver')
os.environ.setdefault('COOKIE_SECURE', 'false')

from app.main import app, limiter
from app.security import hash_password

PRODUCT_ID = '10000000-0000-4000-8000-000000000001'


class FakeDB:
    """API 경계/권한 테스트용 대역. SQL 트랜잭션 검증은 test_postgres.py에서 수행."""
    def __init__(self):
        self.users = []
        self.calls = []
        self.product = {'id': PRODUCT_ID, 'name': '테스트 머그', 'description': '상품 설명',
                        'category': '키친', 'price': 18000, 'stock': 40, 'image_key': 'mug'}

    def close(self):
        pass

    def select(self, table, **params):
        self.calls.append(('select', table, params))
        if table == 'products':
            if params.get('id', f'eq.{PRODUCT_ID}') != f'eq.{PRODUCT_ID}':
                return []
            return [copy.deepcopy(self.product)]
        if table == 'users':
            return [copy.deepcopy(u) for u in self.users if all(
                str(u.get(k)).lower() == str(v)[3:].lower() for k, v in params.items() if k not in ('select', 'limit'))]
        return []

    def request(self, method, table, data=None, **kwargs):
        if method == 'POST' and table == 'users':
            if any(u['email'] == data['email'] for u in self.users):
                raise HTTPException(409, '이미 등록된 정보입니다.')
            user = {**data, 'id': str(uuid4()), 'token_version': 0, 'is_active': True,
                    'created_at': '2026-10-29T00:00:00Z'}
            self.users.append(user)
            return [copy.deepcopy(user)]
        raise AssertionError('Unexpected request')

    def mutate(self, user, action, data=None):
        self.calls.append(('mutate', action, data))
        stored = next(u for u in self.users if u['id'] == user['id'])
        if action == 'logout':
            stored['token_version'] += 1
            return {}
        if action == 'profile':
            stored.update(data)
            if 'password_hash' in data:
                stored['token_version'] += 1
            return copy.deepcopy(stored)
        if action == 'delete_account':
            stored['is_active'] = False
            stored['token_version'] += 1
            return {}
        return {'action': action, 'data': data}


@pytest.fixture
def db():
    return FakeDB()


@pytest.fixture
def client(db):
    # HTTP 클라이언트 생성 후 즉시 대역으로 교체하며 원격 요청은 보내지 않습니다.
    app.state.db = db
    limiter.buckets.clear()
    with TestClient(app, base_url='http://testserver') as client:
        app.state.db.close()
        app.state.db = db
        yield client


@pytest.fixture
def headers(client):
    token = client.get('/api/csrf').json()['csrf_token']
    return {'X-CSRF-Token': token, 'Origin': 'http://testserver'}


@pytest.fixture
def signed_in(client, headers):
    response = client.post('/api/auth/register', headers=headers, json={
        'email': 'member@example.com', 'password': 'correct-pass123', 'name': '테스트 회원',
        'phone': '010-1234-5678', 'address': '서울시 테스트로 123'})
    assert response.status_code == 201
    return response.json()['user']
