# 1차시. Swagger와 OpenAPI: 문서에 없는 API 찾기

> 오늘의 핵심 질문: 주소로 호출되는 API가 왜 Swagger 목록에는 없을까요?

## 오늘 할 일

- 목표: Swagger 화면과 OpenAPI 명세, 실제 HTTP 호출을 구분하고 누락된 경로를 복구한다.
- 선수 지식: 함수, import, 딕셔너리, 문자열. HTTP는 이번 차시에 처음 배워도 됩니다.
- 산출물: Swagger 실행 결과 2개와 OpenAPI 경로 비교표
- 수업: 50분. Python 설치·패키지 설치·편집기 준비는 아래 사전 준비 시간으로 분리합니다.
- 범위: 로컬 FastAPI 한 개입니다. 유료 AI·API 키 없이 제공 코드와 테스트만으로 핵심 실습이 가능합니다. AI 도구가 있으면 CODEX_PROMPTS.md로 분석을 돕습니다.

## 50분 진행

| 시간 | 활동 |
| --- | --- |
| 0–5분 | 핵심 질문·비유·입력 결과 예상 |
| 5–15분 | 업무 계약·Swagger·핵심 코드 읽기 |
| 15–28분 | 정상 실행·의도한 오류 재현·실제 결과 기록 |
| 28–40분 | AI 테스트 생성·분석·최소 수정 |
| 40–47분 | 같은 테스트 재실행·수정 전후 비교 |
| 47–50분 | 이해도 확인·제출 |


## 개념을 코드에 연결하기

카페의 메뉴판이 Swagger이고 메뉴판을 만드는 데이터가 OpenAPI입니다. 메뉴판에서 음료를 숨겨도 바리스타에게 직접 주문하면 제조할 수 있습니다. include_in_schema는 메뉴판 표시 여부이며 요청 허용 여부가 아닙니다.

API는 프로그램끼리 요청과 응답을 주고받는 약속입니다. GET은 조회, POST는 본문을 보내 처리하는 요청입니다. 경로는 주소의 / 뒤 부분이고 상태 코드는 처리 결과를 나타냅니다. 200은 일반 성공, 201은 이 수업의 생성 성공, 404는 없는 자원, 409는 이 수업의 좌석 충돌, 422는 기본 입력 검증 실패에 사용합니다. 실제 구현한 상태만 이번 차시에서 확인합니다.

Swagger UI는 사람이 실행해 보는 화면이고 OpenAPI는 기계가 읽는 API 설명 데이터입니다. 화면의 Responses 설명이나 Example Value는 실제 실행 결과가 아닙니다. Execute 후 Server response를 확인하세요. 문서 생성은 기능 검증을 대신하지 않습니다.

## 업무 계약: 기대값의 근거

GET /greet는 공개 문서에 보여야 합니다. name을 생략하면 guest, name=Min이면 Min에게 인사합니다. 응답은 message 한 항목이며 상태는 200입니다.

기대값은 현재 구현에서 복사하지 않고 위 계약에서 정합니다. TEST_CASES.md의 각 행에서 먼저 결과를 예상한 뒤 실행합니다.

## 사전 준비 — 수업 50분에서 제외

Windows CMD 기준, ZIP을 풀어 **이 README와 main.py가 함께 있는 폴더**에서 실행합니다. 경로에 공백이 있으면 따옴표로 감쌉니다. Python 3.12로 검증했습니다. 다른 Python 버전은 별도 확인이 필요합니다.

```bat
cd /d "C:\AI4\lesson_01_swagger"
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python --version
```

위 C:\AI4 경로는 예시입니다. 실제 압축을 푼 폴더로 바꾸세요. requirements.txt는 재현성을 위해 선택한 검증 버전이며 최신 버전을 뜻하지 않습니다. 하위 의존성까지 고정한 완전한 잠금 파일도 아닙니다. fastapi는 서버 프레임워크, pydantic은 모델·검증, uvicorn은 실제 HTTP 서버, httpx는 TestClient 실행, pytest는 제공 검사의 실행에 필요합니다. 전부 이번 실습에서 사용합니다.

PowerShell은 `.venv\Scripts\Activate.ps1`, macOS/Linux는 `python3 -m venv .venv` 후 `source .venv/bin/activate`를 사용합니다. PowerShell 활성화가 막히면 CMD를 쓰거나 `.venv\Scripts\python.exe`로 직접 실행하세요. macOS/Linux에서 아래 copy는 cp로 바꿉니다.

## 파일을 읽는 순서

1. README.md: 수업 진행과 실행 안내.
2. CODE_GUIDE.md: 생략 없는 학생·검사 코드와 함수별 설명.
3. TEST_CASES.md: 계약에서 도출한 입력·기대값 표.
4. main.py: 의도한 오류가 있는 학생 시작 서버.
5. test_api.py: 정상·오류·회귀를 확인하는 제공 테스트. 1~3차시는 준비된 검사 도구로 사용하고 4차시부터 구조를 직접 읽습니다.
6. CODEX_PROMPTS.md: 테스트 생성 → 분석 → 최소 수정 → 검토 활동.
7. CHECKLIST.md: 제출·자기 점검.
8. 정답 확인 시에만 TEACHER.md와 solution.py를 엽니다.
9. VERIFICATION.md: 제작 환경의 실제 실행 결과와 미검증 한계.
10. SOURCES.md: 공식 동작을 확인한 문서.
11. lesson_scope.json: 강사용 파일·경로 범위 검증 자료이며 학생 실행 코드가 아닙니다.


## 실행 1 — 서버와 Swagger

터미널 A에서 가상환경을 활성화한 뒤 실행합니다.

```bat
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
```

`Application startup complete`를 확인합니다. 브라우저에서 http://127.0.0.1:8000/docs 를 열고, 명세 원문은 http://127.0.0.1:8000/openapi.json 에서 확인합니다. 자동 제공 경로이며 main.py에 직접 구현한 학습 API와 구분합니다. Swagger의 JS/CSS는 기본 CDN에서 가져오므로 화면을 표시하려면 인터넷 연결이 필요할 수 있습니다. 로컬 API와 TestClient 검사는 외부 서비스·API 키가 필요 없습니다.

브라우저에서 http://127.0.0.1:8000/greet?name=Min 을 먼저 엽니다. 이어 /docs를 열어 GET /greet를 찾습니다. 시작 코드에서는 목록이 비어 있습니다. /openapi.json의 paths도 확인합니다. 수정 후 서버를 재시작하고 GET /greet → Try it out → name에 Min → Execute를 누릅니다. Request URL, Response code, Response body를 기록합니다.

터미널 B에서도 같은 폴더와 가상환경을 사용합니다. CMD에서 다음 요청으로 실제 서버 응답을 확인할 수 있습니다.

```bat
curl.exe "http://127.0.0.1:8000/greet?name=Min"
```

위 curl.exe의 따옴표는 Windows CMD 기준입니다. 다른 셸의 인용 규칙이 다르면 Swagger에서 같은 JSON을 보내세요. POST 본문은 주소창에서 직접 보내지 못합니다.

| 서버·포트 | 메서드 | 직접 선언 경로 | 실제 호출 주체 | 실행 함수 | 계약상 응답 |
| --- | --- | --- | --- | --- | --- |
| 127.0.0.1:8000 | GET | /greet | test_api.py 및 Swagger Execute | greet | 200 |


`@app.get`·`@app.post`는 모듈을 읽을 때 경로를 등록합니다. 함수 본문은 해당 HTTP 요청이 들어올 때 실행됩니다. 요청 모델·Path·Query 검증에 실패하면 경로 함수 전에 422로 응답합니다. 이 차시에는 사용자 정의 lifespan이나 시작 콜백이 없습니다.

## 실행 2 — 예상 → 오류 재현 → 비교

1. TEST_CASES.md에서 정상 1개와 오류 1개의 상태·본문을 먼저 예상합니다.
2. Swagger에서 실제 결과를 실행하고 입력과 결과를 함께 기록합니다.
3. 터미널 B에서 제공 검사를 실행합니다.

```bat
python -m pytest -q test_api.py
```

시작 코드에서는 일부 검사가 **의도적으로 실패**합니다. 오류 메시지의 expected(기대)와 actual(실제)을 읽습니다. 현재 결함의 최소 검사 명령은 다음과 같습니다.

```bat
python -m pytest -q test_api.py::test_document_transport
```

- 기대: 업무 계약과 TEST_CASES.md의 상태·데이터.
- 시작 코드 실제 증상: GET /greet는 200으로 동작하지만 /openapi.json의 paths에 없어 /docs에도 나타나지 않습니다.
- 관찰할 점: 같은 요청을 보냈는지, 상태만 맞는지, 본문·문서·이후 요청까지 맞는지 확인합니다.

TestClient는 main의 app에 프로세스 안에서 요청을 보내며 8000번 네트워크 서버에 연결하지 않습니다. pytest 실행에는 Uvicorn이 없어도 됩니다. Swagger에서 쓰는 서버와 TestClient의 메모리 데이터는 별개입니다.

## 실행 3 — AI와 최소 수정

터미널 A가 실행 중일 때 명세를 파일로 저장하면 AI에게 실제 문서도 함께 줄 수 있습니다. 이 파일은 실행해서 생기는 학생 관찰 자료이며 배포 시작 파일에는 없습니다.

```bat
curl.exe "http://127.0.0.1:8000/openapi.json" -o openapi_snapshot.json
```

명세는 현재 구현을 설명하므로 의도한 결함도 반영될 수 있습니다. 이 파일과 업무 계약을 대조하여 어느 쪽을 바꿔야 하는지 판단합니다.

CODEX_PROMPTS.md의 테스트 생성 → 분석 → 최소 수정 → 검토 순서를 따릅니다. AI가 만든 표는 TEST_CASES.md와 비교하고, 테스트 코드는 별도 test_generated.py로 저장해 검사합니다. 실제 서버·제공 테스트를 먼저 읽고 계약과 다른 기대값이 없는지 검토하세요. AI 이용이 어렵다면 제공 표·검사를 동료와 검토하여 같은 활동을 수행합니다.

수정한 main.py로 `python -m pytest -q test_api.py`를 다시 실행합니다. Swagger는 터미널 A에서 Ctrl+C로 서버를 종료 후 같은 명령으로 재시작하고 브라우저 새로고침 후 다시 Execute합니다. 이번 서버 명령에는 자동 재시작 옵션이 없습니다.

정답과 비교하려면 시작 코드를 보관한 뒤 적용합니다. 이는 자신이 수정하기 전에 하는 명령이 아니라 **정답 확인 단계**입니다.

```bat
copy main.py main_before.py
copy /Y solution.py main.py
python -m pytest -q test_api.py
```

main_before.py는 학생 로컬 백업이며 배포 ZIP에는 없습니다. 정답 코드 전체와 변경 이유는 TEACHER.md에 있습니다. 테스트를 지우거나 기대값을 잘못된 결과에 맞추지 않습니다.

## 막힐 때

- `No module named ...`: 터미널 A/B의 `python -m pip --version`과 가상환경을 확인하고 requirements를 설치합니다.
- `Could not import module main`: main.py가 있는 폴더에서 실행했는지 봅니다.
- 8000 포트 사용 중: 이전 서버를 Ctrl+C로 종료합니다. 다른 포트를 쓰면 브라우저·curl 주소도 모두 바꿉니다.
- 브라우저 404: 루트 /가 아니라 위 학습 경로 또는 /docs를 엽니다. 이번 차시에 사용하지 않는 루트·health API는 없습니다.
- 수정해도 그대로: 서버를 재시작하고 OpenAPI 명세·브라우저를 새로고침합니다.
- pytest 전부 수집 금지: 과정 전체 루트에서 실행하지 말고 **차시 폴더 안**에서 `test_api.py`를 지정합니다. 각 lesson은 main이라는 같은 모듈명을 독립적으로 씁니다.
- 초록색 200 표시: 성공 상태만으로 데이터·업무 규칙까지 맞는 것은 아닙니다.

## 이해도 확인 — 답은 TEACHER.md

1. GET 데코레이터를 읽는 순간 greet가 실행되나요?
2. 문서에 숨기면 외부에서 호출할 수 없나요?
3. /docs의 200만 확인하면 충분한가요?

## 제출과 평가

main.py, 자신이 검토·추가한 테스트(test_generated.py를 만들었다면 함께), 테스트표, REPORT_TEMPLATE.md를 채운 보고서를 제출합니다. 실제 요청·수정 전 실패·수정 후 결과를 넣고 AI 제안 중 채택/거절한 항목과 이유를 적으세요. CHECKLIST.md로 마무리합니다.

- 계약 기반 기대값·테스트 범위 30점
- 재현과 원인 근거 25점
- 최소 수정·정상 보존 25점
- 실제 재실행 증거·한계·AI 검토 20점

총 80점 이상이고 제공 회귀 검사 통과, 오류 재현 근거가 있으면 완료입니다. 강사 결과를 자신의 실행 결과처럼 제출하지 않습니다.

선택 심화는 요청되지 않아 코드·추가 활동을 포함하지 않았습니다. 다음 개념: 경로 변수와 쿼리 변수, 기본값을 확인합니다.
