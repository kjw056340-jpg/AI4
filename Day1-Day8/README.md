# 작은 방명록

Day1~Day8에서 사용한 Python·FastAPI·Pydantic을 유지한 HTML 중심 방명록입니다.
모든 새 코드·문서는 이 `Day1-Day8` 폴더에 있습니다. 기존 수업 파일은 수정하지 않았습니다.

## 구현 범위

- 작성자와 내용을 등록하고 최신 글부터 조회합니다.
- 한 페이지에 20개, 전체 최대 1,000개입니다. 가득 차면 기존 글을 보존하고 등록을 거절합니다.
- 작성자는 앞뒤 공백 제거 후 1~20자, 내용은 1~1000자입니다.
- SQLite 테이블은 `guestbook` 하나입니다. 관계·회원 테이블이 없습니다.
- 화면은 서버가 만드는 HTML과 로컬 CSS뿐입니다. JavaScript, React, Vue, CDN이 없습니다.
- 로그인·수정·삭제·첨부파일·검색·외부 API는 이번 기본 범위에 포함하지 않았습니다.

## 실행

Python 3.13을 권장하며 3.12도 사용할 수 있습니다. 현재 고정된 패키지는 Python 3.14와 호환되지 않습니다.
Render용 `.python-version`에는 `3.13`을 지정했습니다. 아래 PowerShell 명령은 저장소 루트에서 시작합니다.
이미 이 폴더에 있다면 첫 `cd`는 생략합니다.

```powershell
cd Day1-Day8
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
```

Python 3.12가 설치되어 있다면 첫 Python 명령을 `py -3.12 -m venv .venv`로 바꾸세요.
`py`를 찾지 못하면 Python 설치 경로를 확인해야 합니다. 기존 가상환경이 삭제된 Python을 가리킨다면 새로 만드세요.

브라우저에서 <http://127.0.0.1:8000/>를 엽니다. 종료는 터미널에서 `Ctrl+C`입니다.
첫 서버 시작 때 `data/guestbook.sqlite3` 파일과 테이블을 자동으로 만듭니다.
같은 파일을 사용하면 서버 재시작 후에도 글이 남습니다. 파일 자체가 삭제되면 복구되지 않습니다.

Linux/macOS에서는 `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`,
`.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1`을 사용합니다.

## 파일 읽는 순서

| 파일 | 내용 |
| --- | --- |
| `ANALYSIS.md` | 원본 수업의 문법·알고리즘 분석과 채택 이유 |
| `index.html`, `style.css` | 입력 폼과 목록의 최소 화면 |
| `schema.sql` | 단일 테이블 정의 |
| `main.py` | 입력 검증 → DB 저장 → HTML 응답 |
| `test_guestbook.py` | 정상·경계·오류·동시 등록 검사 |
| `DEPLOYMENT.md` | 무료 배포 조건과 서비스별 제약 |
| `VERIFICATION.md` | 실제 검증 환경·결과·남은 한계 |

## 요청과 데이터

| 요청 | 동작 | 결과 |
| --- | --- | --- |
| `GET /?page=1` | 최신순 목록 | HTML 200 |
| `POST /entries` | HTML 폼의 `name`, `message` 저장 | 성공 303 → `/` |
| `GET /style.css` | 로컬 스타일 | CSS 200 |

잘못된 입력은 422, 지원하지 않는 폼 형식은 415, 저장 한도 도달은 409,
DB 사용 실패는 503입니다. 페이지 번호는 1~50입니다.
필수 입력 누락 및 요청 파싱 단계의 오류는 422가 우선할 수 있습니다.
오류 화면에서 입력을 수정해 다시 등록하거나 `처음` 링크로 목록에 돌아갑니다.
작성 시각은 서버의 지역 설정과 무관하게 UTC로 저장·표시합니다.

`guestbook`의 열은 `id INTEGER PRIMARY KEY`, `name TEXT`, `message TEXT`, `created_at TEXT`입니다.
자동 증가 번호는 SQLite의 INTEGER PRIMARY KEY 기능으로 만듭니다. 별도 시퀀스 테이블은 없습니다.

## 테스트

이 폴더 안에서 실행하세요. 원본 수업은 학습용 오류를 포함하므로 저장소 전체 테스트와 섞지 않습니다.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q test_guestbook.py
```

테스트는 임시 DB를 사용하므로 실제 방명록 파일에 글을 쓰지 않습니다.
운영에는 `requirements.txt`만 설치하면 됩니다. 개발 패키지도 Day8에서 사용하던 것과 같은 종류·버전입니다.

## DB 경로와 백업

기본 경로는 이 코드 폴더 아래 `data/guestbook.sqlite3`입니다.
영구 저장 경로가 따로 제공되는 호스팅에서는 `GUESTBOOK_DB_PATH`를 절대 경로로 설정할 수 있습니다.

```powershell
$env:GUESTBOOK_DB_PATH = 'C:\Users\Playdata\dev\Day1-Day8\data\guestbook.sqlite3'
```

간단한 수동 백업은 서버를 종료한 다음 DB 파일을 다른 안전한 위치에 복사하는 방식입니다.
DB와 `.verification` 임시 검증 파일은 Git에서 제외됩니다.

## 무료 배포 전제

**무료 실행과 SQLite 데이터 영구 보존은 별개의 조건입니다.**
현재 확인한 서비스 제약과 명령은 [DEPLOYMENT.md](DEPLOYMENT.md)에 있습니다.
무료 영구 저장이 확인되지 않은 서비스를 운영용으로 확정하지 않았으며 실제 배포도 수행하지 않았습니다.
추가 라이브러리, DB 서비스, 인증 기능 또는 다른 프레임워크가 필요해지면 먼저 사용자와 협의합니다.
