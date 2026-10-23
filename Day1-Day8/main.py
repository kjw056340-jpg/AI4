"""Day1~Day8에서 배운 문법으로 만든 HTML 방명록."""

import os
import sqlite3
from contextlib import asynccontextmanager, closing
from html import escape
from pathlib import Path
from string import Template
from typing import Annotated
from urllib.parse import parse_qs

from fastapi import Body, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

BASE_DIR = Path(__file__).resolve().parent
PAGE_SIZE = 20
MAX_ENTRIES = 1000
MAX_FORM_BYTES = 16384


class EntryIn(BaseModel):
    # Day6: 앞뒤 공백을 제거한 다음 길이를 검사합니다.
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=20)
    message: str = Field(min_length=1, max_length=1000)


def connect_db(db_path: Path):
    # 연결은 요청별로 만들고 closing으로 반드시 닫습니다.
    connection = sqlite3.connect(db_path, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def render_page(rows=(), page=1, total=0, notice="", name="", message=""):
    cards = []
    for row in rows or ():
        # 사용자 문자열은 HTML로 실행되지 않도록 변환합니다.
        cards.append(
            '<article class="entry">'
            f'<header><strong>{escape(row["name"])}</strong>'
            f'<time>{escape(row["created_at"])} UTC</time></header>'
            f'<p>{escape(row["message"])}</p></article>'
        )
    if not cards:
        text = "저장된 글은 처음 링크에서 확인할 수 있습니다." if rows is None else "아직 남겨진 글이 없습니다."
        cards.append(f'<p class="empty">{text}</p>')
    links = []
    if page > 1:
        links.append(f'<a href="/?page={page - 1}">이전</a>')
    if total is not None and page * PAGE_SIZE < total:
        links.append(f'<a href="/?page={page + 1}">다음</a>')
    template = Template((BASE_DIR / "index.html").read_text(encoding="utf-8"))
    return template.substitute(
        entries="\n".join(cards), navigation=" ".join(links), page=page,
        count_label="" if total is None else f"총 {total}개",
        notice=escape(notice), name=escape(name), message=escape(message),
    )


def error_page(notice: str, status_code: int, name="", message=""):
    return HTMLResponse(
        render_page(rows=None, total=None, notice=notice, name=name, message=message),
        status_code=status_code,
    )


def create_app(db_path: Path | None = None):
    database = Path(db_path) if db_path is not None else Path(
        os.environ.get("GUESTBOOK_DB_PATH", str(BASE_DIR / "data" / "guestbook.sqlite3"))
    )

    @asynccontextmanager
    async def lifespan(app):
        database.parent.mkdir(parents=True, exist_ok=True)
        with closing(connect_db(database)) as connection:
            with connection:
                connection.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))
        yield

    # 공개 화면은 HTML만 사용합니다. Swagger의 외부 JS/CDN도 불러오지 않습니다.
    app = FastAPI(title="작은 방명록", lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def response_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; style-src 'self'; form-action 'self'; "
            "base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, exc):
        return error_page("페이지 번호 또는 전송한 입력을 확인해주세요.", 422)

    @app.exception_handler(sqlite3.Error)
    async def database_error(request, exc):
        return error_page("저장소를 사용할 수 없습니다. 잠시 후 다시 시도해주세요.", 503)

    @app.get("/style.css")
    def stylesheet():
        return FileResponse(BASE_DIR / "style.css", media_type="text/css")

    @app.get("/", response_class=HTMLResponse)
    def index(page: Annotated[int, Query(ge=1, le=50)] = 1):
        with closing(connect_db(database)) as connection:
            total = connection.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0]
            rows = connection.execute(
                "SELECT name, message, created_at FROM guestbook "
                "ORDER BY id DESC LIMIT ? OFFSET ?",
                (PAGE_SIZE, (page - 1) * PAGE_SIZE),
            ).fetchall()
        return render_page(rows, page, total)

    @app.post("/entries", response_class=HTMLResponse)
    def add_entry(
        request: Request,
        body: Annotated[bytes, Body(media_type="application/x-www-form-urlencoded",
                                    max_length=MAX_FORM_BYTES)],
    ):
        if request.headers.get("content-type", "").split(";")[0].strip().lower() != (
            "application/x-www-form-urlencoded"
        ):
            return error_page("HTML 작성 폼으로 글을 보내주세요.", 415)
        # 추가 패키지 python-multipart 대신 표준 라이브러리로 기본 폼만 처리합니다.
        try:
            fields = parse_qs(body.decode("utf-8"), keep_blank_values=True,
                              strict_parsing=True, errors="strict", max_num_fields=2)
            if set(fields) != {"name", "message"} or any(len(v) != 1 for v in fields.values()):
                raise ValueError("잘못된 폼 필드")
        except (UnicodeError, ValueError):
            return error_page("작성자와 내용을 올바르게 보내주세요.", 422)
        name, message = fields["name"][0], fields["message"][0]
        try:
            entry = EntryIn(name=name, message=message)
        except ValidationError:
            return error_page("작성자는 1~20자, 내용은 1~1000자로 입력해주세요. 공백만 쓸 수 없습니다.",
                              422, name, message)
        with closing(connect_db(database)) as connection:
            with connection:
                # 개수 확인과 저장을 한 트랜잭션으로 묶어 동시 요청에도 한도를 지킵니다.
                connection.execute("BEGIN IMMEDIATE")
                total = connection.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0]
                if total >= MAX_ENTRIES:
                    return error_page("방명록이 가득 찼습니다. 운영자에게 문의해주세요.", 409, name, message)
                # SQL 문법과 입력값을 분리합니다. 문자열을 SQL에 붙이지 않습니다.
                connection.execute(
                    "INSERT INTO guestbook (name, message) VALUES (?, ?)",
                    (entry.name, entry.message),
                )
        # 새로고침 시 POST 재전송을 피하도록 목록으로 이동합니다.
        return RedirectResponse("/", status_code=303)

    return app


app = create_app()
