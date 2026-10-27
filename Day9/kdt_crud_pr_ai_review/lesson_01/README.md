# 1차시 | CRUD 통합의 시작: 조회와 등록을 하나의 FastAPI에 연결

**핵심 질문:** 조회 기능과 등록 기능이 하나의 데이터 목록을 공유할 때 어떤 오류가 생길까?

**목표:** GET/POST 요청을 읽고 실행하며, 등록 후 ID 중복을 재현하고 최소 수정한다.

**선수 지식:** 파이썬 리스트·딕셔너리·함수, HTTP GET/POST, FastAPI의 데코레이터와 Pydantic 기본, Git `status`·`add`·`commit` 기초.

**산출물:** 실행한 API, 오류 재현 로그, 수정 내역 설명, 검사 성공 화면.

## 50분 진행

| 분 | 활동 |
| --- | --- |
| 0–5 | 식당 주문번호 비유, 오류 예측 |
| 5–15 | 두 경로와 공유 리스트, helper 코드 읽기 |
| 15–28 | 서버 실행, Swagger 요청, 검사 실패 재현 |
| 28–40 | Codex 원인 분석→최소 수정→리뷰 |
| 40–47 | 수정 후 재검사, 전후 비교 |
| 47–50 | 질문 3개, 제출 |

## 실행 환경 — 설치 시간은 수업 50분과 별도

Windows CMD에서 `lesson_01` 폴더로 이동한 뒤:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

터미널 A(서버):

```bat
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
```

`Uvicorn running on http://127.0.0.1:8000` 문구로 준비 완료를 확인한다. 웹브라우저 `http://127.0.0.1:8000/docs`에서 GET `/tasks` 실행 후 POST `/tasks`에 `{"title":"PR 준비"}` 전송. **데코레이터는 경로 등록이고 실제 함수 실행은 HTTP 요청 때 일어난다.** `/docs`와 `/openapi.json`은 FastAPI 자동 생성 문서이지 우리가 직접 선언한 API가 아니다.

터미널 B(독립 검사, 서버 필요 없음):

```bat
python check.py main
python check.py solution
```

`check.py`는 TestClient로 HTTP 요청을 시뮬레이션하며 서버를 띄우지 않는다. 앞선 명령은 의도대로 실패하고 두 번째는 통과한다. `assert`는 조건이 틀리면 즉시 멈춘다.

학생 수정 방법: `main.py`의 `next_id()` 한 줄을 정답 원리를 참고하여 직접 수정 후 `python check.py main` 재실행. 서버 실행 중 파일을 수정했다면 Ctrl+C로 종료 후 위 서버 명령으로 다시 실행한다. 강사용 정답 서버를 직접 보려면 터미널 A에서 기존 서버 종료 후 `python -m uvicorn solution:app --host 127.0.0.1 --port 8000 --workers 1`. 학습 종료 시 Ctrl+C.

macOS/Linux는 `python3 -m venv .venv`, `source .venv/bin/activate`를 사용한다.

## 요청 경로와 관찰

| 요청 | 실제 호출자 | 함수 | 기대 |
| --- | --- | --- | --- |
| GET http://127.0.0.1:8000/tasks | Swagger 또는 `check.py`의 `client.get` | `list_tasks` | 200, 초기 ID `[1,3]` |
| POST http://127.0.0.1:8000/tasks | Swagger 또는 `check.py`의 `client.post` | `create_task` → `next_id` | 201, 신규 ID 4 |

초기 ID가 1, 3이라서 목록 개수 2 + 1은 3입니다. 이미 존재하는 3과 충돌합니다. 레스토랑의 **주문 건수**를 **다음 주문번호**로 잘못 쓰면 번호가 중복되는 것과 같습니다. 이 예제는 데이터베이스 대신 프로세스 메모리의 리스트를 사용합니다. 실행을 재시작하면 데이터가 초기화되며 여러 worker를 사용하지 않습니다.

### 파일 역할

- `main.py`: 학생용 GET/POST API 및 현재 재현할 버그. `python -m uvicorn main:app ...`으로 로딩됨.
- `solution.py`: 같은 두 API의 교사용 최소 정답. `python check.py solution`에서 로딩됨.
- `check.py`: 두 API에 실제 요청을 보내 기대 동작과 실패를 검사. `python check.py main` 또는 `solution`.
- `requirements.txt`: 이 차시 실행에 직접 사용하는 FastAPI/Uvicorn/httpx 설치.
- `CODE_GUIDE.md`: 코드 줄별 동작 해설.
- `CODEX_PROMPTS.md`: AI 분석→수정→검토 순서.
- `TEACHER.md`: 답안, 확인 질문, 평가 기준.
- `VERIFICATION.md`: 개발 환경에서 확인한 검사 결과.
- `lesson_scope.json`: 강사용 코드 범위 감사 자료, 학생 실행에 사용하지 않음.

**제출:** 실패 로그 1장, 수정 후 통과 로그 1장, 오류 원인 2문장, Codex 제안에 대해 직접 확인한 사항 1개.

**다음 차시 예고:** 개별 조회와 없는 항목 처리 (코드는 2차시에 작성).
