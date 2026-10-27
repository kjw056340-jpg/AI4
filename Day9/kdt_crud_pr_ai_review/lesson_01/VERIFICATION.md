# 제작 환경 검증 기록

- 확인 환경: Python 3, FastAPI 0.128.2, httpx 0.28.1, uvicorn 0.48.0.
- `python check.py main`: **예상된 실패**, 종료 코드 1. GET=200, POST=201, 초기 ID `[1,3]`, 생성 ID=3, 최종 ID `[1,3,3]`, 중복 ID AssertionError.
- `python check.py solution`: **정상 통과**, 종료 코드 0. GET=200, POST=201, 생성 ID=4, 최종 ID `[1,3,4]`, `PASS` 출력.
- `TestClient(main.app).post('/tasks', json={'title':''})`: **422** 확인.
- `python /home/oai/skills/kdt-lesson-builder/scripts/audit_lesson_scope.py lesson_01`: **PASS** (파일 명세, 직접 선언 경로, 인용 근거, 기본 AST 점검).
- 수동 의미 검사: `check.py`의 실제 GET/POST 요청에 main/solution의 각 경로 연결됨. `next_id`는 POST에서만 호출. 미사용 import·지역변수·차시 외 API·기본 불필요 패키지 없음. 별도 mock 서버 없음.
- 제한: 외부 GitHub 실제 계정과 PR 생성은 1차시 범위가 아니므로 검증하지 않음. Uvicorn의 실제 HTTP 포트 접속은 별도 실측하지 않았으며, TestClient 요청을 통한 FastAPI 동작을 검증함.

`lesson_scope.json`은 **강사용 범위 검증 메타데이터**로 학생 실행에 쓰이지 않습니다. 정적 PASS는 의미 검증 전체를 자동 증명하지 않습니다.
