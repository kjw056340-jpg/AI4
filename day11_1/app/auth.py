"""Stateless Supabase Auth transport: never shares a user's session across requests."""
import httpx
from fastapi import HTTPException

from app.config import Settings


class Auth:
    def __init__(self, settings: Settings):
        self.key = settings.supabase_key
        self.client = httpx.Client(base_url=f'{settings.supabase_url}/auth/v1/',
                                   headers={'apikey': settings.supabase_key}, timeout=15)

    def close(self):
        self.client.close()

    def request(self, method, path, *, data=None, token=None, params=None):
        try:
            response = self.client.request(method, path, json=data, params=params,
                headers={'Authorization': f'Bearer {token}'} if token else {})
        except httpx.RequestError:
            raise HTTPException(503, '인증 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.') from None
        if response.is_error:
            if response.status_code == 429:
                raise HTTPException(429, '인증 요청이 많습니다. 잠시 후 다시 시도해 주세요.')
            if response.status_code >= 500:
                raise HTTPException(503, '인증 서버가 응답하지 않습니다. 잠시 후 다시 시도해 주세요.')
            if path == 'signup':
                raise HTTPException(400, '가입하지 못했습니다. 이메일 인증 상태와 비밀번호 정책을 확인해 주세요.')
            raise HTTPException(401, '이메일 또는 비밀번호를 확인하거나 다시 로그인해 주세요.')
        return response.json() if response.content else {}

    def login(self, email, password):
        return self.request('POST', 'token', params={'grant_type': 'password'},
                            data={'email': email, 'password': password})

    def signup(self, data):
        return self.request('POST', 'signup', data=data)

    def user(self, token):
        return self.request('GET', 'user', token=token)

    def refresh(self, token):
        return self.request('POST', 'token', params={'grant_type': 'refresh_token'},
                            data={'refresh_token': token})

    def logout(self, token):
        return self.request('POST', 'logout', token=token, params={'scope': 'global'})

    def password(self, token, password):
        return self.request('PUT', 'user', token=token, data={'password': password})

    def delete_user(self, identity):
        # Soft deletion preserves the FK used by retained order/payment records.
        return self.request('DELETE', f'admin/users/{identity}',
                            token=None if self.key.startswith('sb_secret_') else self.key,
                            data={'should_soft_delete': True})
