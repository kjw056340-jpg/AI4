# 4차시 | DELETE와 전체 CRUD: 삭제 뒤에도 데이터가 일관적인가?

**오늘의 질문:** Task의 ID와 리스트 위치를 혼동하면 무엇이 삭제될까?

**학습 목표:** 현재 차시의 결함을 재현·설명·최소 수정하고, 관련 협업 산출물을 기록한다. **선수 지식:** Python 함수·리스트·딕셔너리, `git status/add/commit`, FastAPI TestClient와 Pydantic.

**실습 산출물:** 실패/성공 검사 로그, 변경 코드 diff, Codex 검토 기록.

## 시간표 (설치/심화는 수업 시간 제외)

| 구간 | 실제 활동 |
|---|---|
| 0–5분 | 식당의 주문번호 비유와 오류 예측 |
| 5–15분 | 주요 함수와 흐름, 기대 결과 읽기 |
| 15–28분 | `python check.py main` 실행, 실패 재현 |
| 28–40분 | Codex 분석→최소 수정 및 Git 변경내역 확인 |
| 40–47분 | 정답 검사, 결과 비교, 정상 회귀 확인 |
| 47–50분 | 퀴즈·작업 결과 제출 |

## 환경 준비 (별도 시간, Windows CMD)

`lesson_04` 폴더로 이동 후 터미널 A:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
```

서버 준비 문구를 확인하고 http://127.0.0.1:8000/docs 에 접속합니다. `/docs`, `/openapi.json`은 FastAPI 자동 제공 문서이며 직접 작성한 경로는 아닙니다. 서버를 수정하면 Ctrl+C로 종료하고 재시작합니다. 서버는 메모리 상태 공유 실습이므로 worker 1개입니다.

터미널 B에서 독립적으로 실행:

```bat
python check.py main
python check.py solution
```

`main`은 의도한 결함 때문에 실패하고 `solution`은 통과해야 합니다. 학생이 `main.py`를 직접 고친 뒤 첫 명령도 통과시키는 것이 과제입니다. macOS/Linux는 `python3 -m venv .venv; source .venv/bin/activate`를 사용합니다.

## 호출 관계

- `GET http://127.0.0.1:8000/tasks`: `check.py`의 `client.get` 호출이 경로 함수를 실제 실행
- `POST http://127.0.0.1:8000/tasks`: `check.py`의 `client.post` 호출이 경로 함수를 실제 실행
- `PUT http://127.0.0.1:8000/tasks/{task_id}`: `check.py`의 `client.put` 호출이 경로 함수를 실제 실행
- `DELETE http://127.0.0.1:8000/tasks/{task_id}`: `check.py`의 `client.delete` 호출이 경로 함수를 실제 실행

`check.py` → `importlib.import_module('main' 또는 'solution')` → TestClient HTTP 요청 → 라우트 함수 호출 → `assert`로 기대값 검증. 단순 데코레이터 등록은 HTTP 요청 실행과 다릅니다.

**오류:** 삭제 시 Task ID를 리스트 인덱스로 간주해 500이 발생한다.  **수정:** ID가 같은 항목의 인덱스를 찾아 삭제하고 없으면 404로 반환한다.

**예상 관찰:** GET [1,3] → POST 4 → PUT 3 → DELETE 3 → GET [1,4]; 없는 ID 404

## 학생 활동과 평가

1. 실패 출력의 실제/기대 차이를 기록합니다.
2. Codex에 먼저 원인을 분석하게 하고, 근거를 코드 줄과 연결합니다.
3. `main.py`만 최소 수정해 재검증하고 `solution.py`와 비교합니다.
4. 실패 로그·통과 로그·diff·원인 설명을 제출합니다.

**평가(10점):** 재현 2, 원인 설명 3, 최소 수정 2, 통과 검사 2, 코드/AI 검토 1. **선택 심화**는 별도 제공하지 않음. 다음 차시: 5차시 개념으로 이동하며 해당 코드는 이 ZIP에 넣지 않았습니다.

## 파일 설명

- `main.py`: 실패를 재현하는 학생 시작 코드. `python check.py main`에서 로딩.
- `solution.py`: 최소 수정 기준 코드. `python check.py solution`에서 로딩.
- `check.py`: 학습 목표를 정상 입력과 오류 입력으로 확인. 별도 명령으로 직접 실행.
- Python 단일 파일 직접 실행: `python main.py` 또는 `python solution.py`로 도우미 함수의 관찰용 입력을 출력할 수 있습니다.
- `requirements.txt`: 현재 API와 TestClient 실행에 필요한 직접 의존성.
- `CODE_GUIDE.md`: 코드 전체, 함수·검사 입력/출력, 수정 연결 설명.
- `CODEX_PROMPTS.md`: 분석/수정/검토 3단계 프롬프트.
- `TEACHER.md`: 강사용 풀이, 질문 답, 평가.
- `VERIFICATION.md`: 실제 실행/범위 감사 로그.
- `lesson_scope.json`: 강사용 코드 범위 감사 메타데이터이며 학생 실행 코드가 아닙니다.
