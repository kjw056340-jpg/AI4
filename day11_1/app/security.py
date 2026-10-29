import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, urlsplit

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, Response

from app.config import Settings, get_settings

COOKIE_NAME = 'ondo_access'
CSRF_COOKIE = 'ondo_csrf'


def allowed_origins(settings: Settings) -> set[str]:
    """로컬 HTTP 개발에서만 같은 포트의 localhost/127.0.0.1을 함께 허용합니다."""
    origins = {settings.app_origin}
    configured = urlsplit(settings.app_origin)
    if (not settings.cookie_secure and configured.scheme == 'http'
            and configured.hostname in {'localhost', '127.0.0.1'}):
        port = f':{configured.port}' if configured.port is not None else ''
        origins.update({f'http://localhost{port}', f'http://127.0.0.1{port}'})
    return origins


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode())
    except (ValueError, TypeError):
        return False


def set_auth(response: Response, user: dict):
    settings = get_settings()
    now = datetime.now(timezone.utc)
    token = jwt.encode({'sub': user['id'], 'ver': user['token_version'], 'iat': now,
                        'exp': now + timedelta(minutes=settings.access_token_minutes),
                        'iss': 'ondo-shop', 'aud': 'ondo-web'}, settings.jwt_secret, algorithm='HS256')
    response.set_cookie(COOKIE_NAME, token, max_age=settings.access_token_minutes * 60,
                        httponly=True, secure=settings.cookie_secure, samesite='lax', path='/')


def clear_auth(response: Response):
    response.delete_cookie(COOKIE_NAME, path='/', secure=get_settings().cookie_secure,
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


def current_user(request: Request, db=Depends(get_db)) -> dict:
    try:
        payload = jwt.decode(request.cookies.get(COOKIE_NAME, ''), get_settings().jwt_secret,
                             algorithms=['HS256'], audience='ondo-web', issuer='ondo-shop',
                             options={'require': ['sub', 'ver', 'iat', 'exp']})
        from uuid import UUID
        user_id = str(UUID(payload['sub']))
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise HTTPException(401, '로그인이 필요합니다.') from None
    users = db.select('users', select='*', id=f'eq.{user_id}', is_active='eq.true', limit='1')
    if not users or users[0]['token_version'] != payload['ver']:
        raise HTTPException(401, '로그인이 만료되었습니다. 다시 로그인해 주세요.')
    return users[0]


def public_user(user: dict) -> dict:
    return {key: user[key] for key in ('id', 'email', 'name', 'phone', 'address', 'created_at')}


def safe_next(value: str | None) -> str:
    if not value or len(value) > 1000:
        return '/products'
    decoded = value
    for _ in range(3):
        decoded = unquote(decoded)
    parsed = urlsplit(decoded)
    if (not decoded.startswith('/') or decoded.startswith('//') or parsed.netloc or parsed.scheme
            or '\\' in decoded or any(ord(c) < 32 for c in decoded)
            or parsed.path not in ('/products', '/product', '/cart', '/checkout', '/account', '/orders')):
        return '/products'
    return decoded
