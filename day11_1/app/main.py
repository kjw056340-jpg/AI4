import logging
import secrets
import threading
import time
from collections import OrderedDict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlencode

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException
from starlette.concurrency import run_in_threadpool

from app.config import get_settings
from app.db import Database
from app.auth import Auth
from app.routes import router
from app.security import CSRF_COOKIE, allowed_origins, current_user, refresh_session, set_auth

BASE = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE / 'templates'))
PROTECTED = {'cart', 'checkout', 'account', 'orders', 'admin'}
PAGES = {'products', 'product', 'login', 'register', *PROTECTED}
AUTH_PATHS = {'/api/auth/login', '/api/auth/register', '/api/auth/refresh'}


class RateLimiter:
    """단일 worker용 로그인 제한. IP 헤더는 신뢰하지 않고 연결 주소를 사용합니다."""
    def __init__(self):
        self.buckets = OrderedDict()
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self.lock:
            bucket = self.buckets.pop(key, deque())
            while bucket and bucket[0] <= now - 60:
                bucket.popleft()
            allowed = len(bucket) < 15
            if allowed:
                bucket.append(now)
            self.buckets[key] = bucket
            if len(self.buckets) > 10000:
                self.buckets.popitem(last=False)
            return allowed


limiter = RateLimiter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database(get_settings())
    app.state.auth = Auth(get_settings())
    yield
    app.state.db.close()
    app.state.auth.close()


app = FastAPI(title='온도 쇼핑몰 API', version='1.0.0', lifespan=lifespan,
              docs_url='/api/docs', redoc_url=None)
app.mount('/static', StaticFiles(directory=str(BASE / 'static')), name='static')
app.include_router(router)


@app.middleware('http')
async def security_headers(request: Request, call_next):
    settings = get_settings()
    response = None
    if request.url.path.startswith('/api/') and request.method not in ('GET', 'HEAD', 'OPTIONS'):
        # Origin 검증과 double-submit 토큰을 로그인/회원가입을 포함해 적용합니다.
        origin = request.headers.get('origin')
        cookie = request.cookies.get(CSRF_COOKIE, '')
        header = request.headers.get('x-csrf-token', '')
        if ((origin and origin not in allowed_origins(settings))
                or request.headers.get('sec-fetch-site') == 'cross-site'
                or len(cookie) != 64 or not secrets.compare_digest(cookie, header)):
            response = JSONResponse({'detail': '보안 확인에 실패했습니다. 새로고침 후 다시 시도해 주세요.'}, 403)
    if response is None and request.url.path in AUTH_PATHS and request.method == 'POST':
        # Render에서는 프록시 주소로 합산될 수 있습니다. 운영 확장 시 공유 제한기를 사용하세요.
        key = request.client.host if request.client else 'unknown'
        if not limiter.allow(key):
            response = JSONResponse({'detail': '요청이 많습니다. 1분 후 다시 시도해 주세요.'}, 429,
                                    headers={'Retry-After': '60'})
    if response is None:
        response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'")
    response.headers['Cache-Control'] = 'no-store' if not request.url.path.startswith('/static/') else 'public, max-age=3600'
    if settings.cookie_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    # 입력값·비밀번호를 응답/로그로 돌려주지 않습니다.
    errors = []
    for error in exc.errors():
        msg = error['msg']
        if msg.startswith('Value error, '):
            msg = msg[len('Value error, '):]
        else:
            msg = '입력 형식 또는 길이를 확인해 주세요.'
        errors.append({'field': str(error['loc'][-1]), 'message': msg})
    return JSONResponse({'detail': '입력 내용을 확인해 주세요.', 'errors': errors}, 422)


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logging.getLogger(__name__).error('Unhandled error: %s', type(exc).__name__)
    return JSONResponse({'detail': '처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'}, 500)


@app.get('/health', include_in_schema=False)
def health():
    return {'status': 'ok'}


@app.get('/', include_in_schema=False)
def home():
    return RedirectResponse('/products', 303)


@app.get('/{page}', include_in_schema=False)
async def screen(page: str, request: Request):
    if page not in PAGES:
        raise HTTPException(404, '페이지를 찾을 수 없습니다.')
    session = None
    if page in PROTECTED:
        try:
            user = await run_in_threadpool(current_user, request, request.app.state.db)
        except HTTPException as exc:
            if exc.status_code != 401:
                raise
            try:
                user, session = await run_in_threadpool(refresh_session, request, request.app.state.db, request.app.state.auth)
            except HTTPException as refresh_error:
                if refresh_error.status_code != 401:
                    raise
                next_url = request.url.path + ('?' + request.url.query if request.url.query else '')
                return RedirectResponse('/login?' + urlencode({'next': next_url}), 303)
        if page == 'admin' and user.get('role') != 'admin':
            raise HTTPException(403, '관리자 권한이 필요합니다.')
    response = templates.TemplateResponse(request=request, name='index.html', context={'page': page})
    if session:
        set_auth(response, user, session)
    return response
