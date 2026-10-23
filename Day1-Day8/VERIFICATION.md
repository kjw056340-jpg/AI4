# 검증 결과

검증일: 2026-10-23 (한국 시간).

## 환경

- Python 공식 임베디드 런타임 3.13.9, SQLite 3.50.4, Windows.
- FastAPI 0.115.12, Pydantic 2.11.5, Uvicorn 0.34.2, httpx 0.28.1, pytest 8.3.5.
- 기존 루트 `.venv`는 존재하지만 원본 Python 실행 경로가 끊겨 있었습니다.
- 검증용 공식 Python은 이 폴더의 `.verification/python`에만 내려받았습니다.
  설치 프로그램을 실행하거나 시스템 PATH를 바꾸지 않았습니다.
- 패키지는 기존 `05.FastAPI-uvicorn/.venv/Lib/site-packages`에 있던 것을 재사용했습니다.
  새 종류의 라이브러리를 설치하지 않았습니다.
- 임시 런타임·DB·서버 로그는 `.verification` 아래에 있고 Git에서 제외됩니다.

## 자동 검사

이 폴더에서 다음 명령으로 실행했습니다.

```powershell
.\.verification\python\python.exe -m pytest -q test_guestbook.py -p no:cacheprovider --basetemp=.verification/test-temp
```

결과: **20 passed**.

검증 범위:

- 실제 HTML form 구조, CSS 응답, JavaScript 태그 없음.
- 작성 → 303 이동, 한글·줄바꿈·특수문자 보존, 공백 제거.
- 같은 DB 파일로 앱을 다시 만들어도 글이 보존됨.
- SQLite 테이블이 `guestbook` 하나뿐임.
- 빈 값·공백·최대 길이·초과 길이, 잘못된 페이지 번호.
- HTML 삽입 문자열의 무해한 출력, SQL 문자열이 실제 SQL로 실행되지 않음.
- 잘못된 폼·필드 누락·중복·과다 필드·잘못된 UTF-8·본문 크기 초과 거부.
- 최신순·20개 단위 페이지 이동.
- 999개 상태에서 동시 두 등록을 보내면 하나만 성공하고 총 1,000개 유지.
- 저장소 오류 시 성공을 표시하지 않고 503 응답.

기존 Starlette TestClient와 anyio 사이에서 `BlockingPortal` 사용에 관한
DeprecationWarning 하나가 발생했습니다. 테스트 실패는 아니며 이번 작업에서는 기존 버전을 변경하지 않았습니다.

## 실제 서버 검사

임시 DB 경로와 빈 로컬 포트로 `python -m uvicorn main:app --workers 1` 프로세스를 띄우고,
Python 표준 HTTP 클라이언트로 아래를 검사한 후 프로세스를 종료했습니다.

- `GET /` → HTML 200.
- `POST /entries` → 이동 후 `GET /`에서 저장한 한글 글 확인.
- `GET /style.css` → CSS 200.

브라우저 조작·스크린샷 검사는 수행하지 않았습니다.

## 저장 크기

별도 임시 DB에 작성자 20자·내용 1,000자의 한글 글 1,000개를 저장했습니다.
결과 파일 크기는 **4,112,384바이트**, 약 **3.92 MiB**였습니다.
이는 한 가지 데이터 구성의 측정값이며 서비스 전체 디스크·메모리·트래픽 사용량을 의미하지 않습니다.

## 아직 확인하지 않은 것

- 실제 무료 호스팅 계정의 배포·재배포·파일 보존·과금 설정.
- Linux 호스팅에서의 실제 실행, 장시간 부하 및 악의적 대량 요청 대응.
- 브라우저별 화면 배치와 모바일 실기기.

무료 서비스의 SQLite 영구 저장 제약은 [DEPLOYMENT.md](DEPLOYMENT.md)에 정리했습니다.
로컬 파일 보존 테스트 통과가 호스팅의 영구 저장을 보장하지는 않습니다.
배포처나 데이터베이스를 임의로 바꾸지 않았습니다.
