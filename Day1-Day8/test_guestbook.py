"""실제 HTML 요청과 임시 SQLite 파일로 기능 및 경계를 확인합니다."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from main import MAX_ENTRIES, create_app


@pytest.fixture
def database(tmp_path):
    return tmp_path / "guestbook.sqlite3"


@pytest.fixture
def client(database):
    with TestClient(create_app(database)) as browser:
        yield browser


def post(client, name="손님", message="반갑습니다!"):
    return client.post("/entries", data={"name": name, "message": message}, follow_redirects=False)


def test_html_form_and_css(client):
    class FormParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.tags = []

        def handle_starttag(self, tag, attrs):
            self.tags.append((tag, dict(attrs)))

    response = client.get("/")
    assert response.status_code == 200
    assert "아직 남겨진 글이 없습니다" in response.text
    parser = FormParser()
    parser.feed(response.text)
    assert ("form", {"action": "/entries", "method": "post", "accept-charset": "UTF-8"}) in parser.tags
    assert not any(tag == "script" for tag, attrs in parser.tags)
    assert client.get("/style.css").status_code == 200
    assert "default-src 'none'" in response.headers["content-security-policy"]


def test_save_redirect_and_persist_after_restart(client, database):
    response = post(client, "  한글 손님  ", "첫 줄\n둘째 줄 & + = %")
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    with TestClient(create_app(database)) as restarted:
        page = restarted.get("/").text
    assert "한글 손님" in page
    assert "첫 줄\n둘째 줄 &amp; + = %" in page
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT name FROM guestbook").fetchone()[0] == "한글 손님"
        assert db.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0] == 1
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    assert tables == [("guestbook",)]


@pytest.mark.parametrize("name,message", [("", "글"), (" \t ", "글"), ("손님", "\n "),
                                           ("가" * 21, "글"), ("손님", "가" * 1001)])
def test_invalid_input_never_saves(client, database, name, message):
    assert post(client, name, message).status_code == 422
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0] == 0


def test_maximum_valid_lengths(client):
    assert post(client, "가" * 20, "나" * 1000).status_code == 303


def test_html_and_sql_injection_are_plain_text(client, database):
    malicious = "<script>alert(1)</script></textarea><img src=x onerror=alert(1)>"
    assert post(client, "');DROP TABLE t;--", malicious).status_code == 303
    page = client.get("/").text
    assert malicious not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert post(client).status_code == 303
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0] == 2


def test_invalid_input_is_escaped_in_form(client):
    response = post(client, "<bad>" * 5, "</textarea><script>bad</script>")
    assert response.status_code == 422
    assert "<script>bad</script>" not in response.text
    assert "&lt;/textarea&gt;" in response.text
    assert "아직 남겨진 글이 없습니다" not in response.text


def test_pagination_and_latest_first(client):
    for number in range(21):
        assert post(client, message=f"글-{number:02d}-끝").status_code == 303
    first, second = client.get("/"), client.get("/?page=2")
    assert first.text.index("글-20-끝") < first.text.index("글-19-끝")
    assert "글-00-끝" not in first.text
    assert "글-00-끝" in second.text
    assert "글-01-끝" not in second.text
    assert 'href="/?page=2"' in first.text
    for page in ["0", "-1", "abc", "51"]:
        assert client.get(f"/?page={page}").status_code == 422


@pytest.mark.parametrize("body", [b"name=a&name=b&message=c", b"name=a", b"name=a&message=b&extra=c",
                                  b"name=%FF&message=b", b"name=a&message", b"name=a&message=" + b"x" * 17000])
def test_malformed_forms(client, body):
    response = client.post("/entries", content=body,
                           headers={"content-type": "application/x-www-form-urlencoded"})
    assert response.status_code == 422


def test_wrong_content_type(client):
    response = client.post("/entries", content=urlencode({"name": "a", "message": "b"}),
                           headers={"content-type": "text/plain"})
    assert response.status_code == 415


def test_capacity_is_atomic_and_preserves_old_entries(client, database):
    with sqlite3.connect(database) as db:
        db.executemany("INSERT INTO guestbook(name,message) VALUES (?, ?)",
                       [("손님", "기존 글")] * (MAX_ENTRIES - 1))
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(lambda _: post(client).status_code, range(2)))
    assert sorted(statuses) == [303, 409]
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0] == MAX_ENTRIES
        assert db.execute("SELECT COUNT(*) FROM guestbook WHERE message='기존 글'").fetchone()[0] == MAX_ENTRIES - 1


def test_storage_failure_does_not_claim_success(client, database):
    with sqlite3.connect(database) as db:
        db.execute("DROP TABLE guestbook")
    response = post(client)
    assert response.status_code == 503
    assert "저장소를 사용할 수 없습니다" in response.text
