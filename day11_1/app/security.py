import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, urlsplit

import jwt
from fastapi import Depends, HTTPException, Request, Response

from app.config import Settings, get_settings

COOKIE_NAME = 'ondo_access'
CSRF_COOKIE = 'ondo_csrf'
SUPABASE_COOKIE = 'ondo_supabase'
REFRESH_COOKIE = 'ondo_refresh'


def allowed_origins(settings: Settings) -> set[str]:
    """로컬 HTTP 개발에서만 같은 포트의 localhost/127.0.0.1을 함께 허용합니다."""
    origins = {settings.app_origin}
    configured = urlsplit(settings.app_origin)
    if (not settings.cookie_secure and configured.scheme == 'http'
            and configured.hostname in {'localhost', '127.0.0.1'}):
        port = f':{configured.port}' if configured.port is not None else ''
        origins.update({f'http://localhost{port}', f'http://127.0.0.1{port}'})
    return origins


def set_auth(response: Response, user: dict, session: dict):
    settings = get_settings()
    now = datetime.now(timezone.utc)
    # This signed envelope only provides immediate shop-session revocation.
    # Identity is always verified separately by Supabase Auth, never by this JWT alone.
    lifetime = 60 * 60 * 24 * 7
    token = jwt.encode({'sub': user['id'], 'ver': user['token_version'], 'iat': now,
                        'access': hashlib.sha256(session['access_token'].encode()).hexdigest(),
                        'refresh': hashlib.sha256(session['refresh_token'].encode()).hexdigest(),
                        'exp': now + timedelta(seconds=lifetime),
                        'iss': 'ondo-shop', 'aud': 'ondo-web'}, settings.jwt_secret, algorithm='HS256')
    response.set_cookie(COOKIE_NAME, token, max_age=lifetime,
                        httponly=True, secure=settings.cookie_secure, samesite='lax', path='/')
    for name, value in ((SUPABASE_COOKIE, session['access_token']), (REFRESH_COOKIE, session['refresh_token'])):
        response.set_cookie(name, value, max_age=lifetime, httponly=True,
                            secure=settings.cookie_secure, samesite='lax', path='/')


def clear_auth(response: Response):
    for name in (COOKIE_NAME, SUPABASE_COOKIE, REFRESH_COOKIE):
        response.delete_cookie(name, path='/', secure=get_settings().cookie_secure,
                               httponly=True, samesite='lax')


def csrf_token(request: Request, response: Response) -> str:
    token = request.cookies.get(CSRF_COOKIE)
    if not token or len(token) != 64:
        token = secrets.token_hex(32)
    response.set_cookie(CSRF_COOKIE, token, secure=get_settings().cookie_secure,
                        httponly=False, samesite='strict', path='/')
    return token


def get_db(request: Request):
    return request.app.state.db


def get_auth(request: Request):
    return request.app.state.auth


def session_user(request: Request, db, *, refreshing=False) -> dict:
    try:
        payload = jwt.decode(request.cookies.get(COOKIE_NAME, ''), get_settings().jwt_secret,
                             algorithms=['HS256'], audience='ondo-web', issuer='ondo-shop',
                             options={'require': ['sub', 'ver', 'iat', 'exp']})
        from uuid import UUID
        user_id = str(UUID(payload['sub']))
        field, cookie = ('refresh', REFRESH_COOKIE) if refreshing else ('access', SUPABASE_COOKIE)
        raw = request.cookies.get(cookie, '')
        if not raw or not secrets.compare_digest(payload[field], hashlib.sha256(raw.encode()).hexdigest()):
            raise ValueError('session mismatch')
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise HTTPException(401, '로그인이 필요합니다.') from None
    users = db.select('users', select='*', id=f'eq.{user_id}', is_active='eq.true', limit='1')
    if not users or users[0]['token_version'] != payload['ver']:
        raise HTTPException(401, '로그인이 만료되었습니다. 다시 로그인해 주세요.')
    return users[0]


def auth_profile(identity: dict, db) -> dict:
    users = db.select('users', select='*', auth_user_id=f"eq.{identity['id']}", is_active='eq.true', limit='1')
    if not users:
        raise HTTPException(401, '사용할 수 없는 계정입니다. 기존 회원은 Auth 계정 연결을 확인해 주세요.')
    return users[0]


def current_user(request: Request, db=Depends(get_db)) -> dict:
    user = session_user(request, db)
    identity = request.app.state.auth.user(request.cookies[SUPABASE_COOKIE])
    if identity['id'] != user.get('auth_user_id'):
        raise HTTPException(401, '로그인이 필요합니다.')
    return user


def refresh_session(request: Request, db, auth):
    user = session_user(request, db, refreshing=True)
    session = auth.refresh(request.cookies[REFRESH_COOKIE])
    if session['user']['id'] != user['auth_user_id']:
        raise HTTPException(401, '로그인이 필요합니다.')
    return user, session


def admin_user(user=Depends(current_user)) -> dict:
    # Role comes from the private profile, never from editable user_metadata.
    if user.get('role') != 'admin':
        raise HTTPException(403, '관리자 권한이 필요합니다.')
    return user


def public_user(user: dict) -> dict:
    return {key: user[key] for key in ('id', 'email', 'name', 'phone', 'address', 'created_at', 'role')}


def safe_next(value: str | None) -> str:
    if not value or len(value) > 1000:
        return '/products'
    decoded = value
    for _ in range(3):
        decoded = unquote(decoded)
    parsed = urlsplit(decoded)
    if (not decoded.startswith('/') or decoded.startswith('//') or parsed.netloc or parsed.scheme
            or '\\' in decoded or any(ord(c) < 32 for c in decoded)
            or parsed.path not in ('/products', '/product', '/cart', '/checkout', '/account', '/orders', '/admin')):
        return '/products'
    return decoded
