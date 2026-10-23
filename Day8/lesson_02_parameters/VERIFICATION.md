# 2차시 제작 실행 검증

검증일: 2026-10-23 (한국 기준). Python 3.12.14 · Linux 실행 환경. 패키지는 requirements.txt에 기록했습니다. 학생 Windows CMD와 브라우저 수동 확인은 README 명령으로 재검증해야 합니다.

## 검증 방식

배포 시작 파일을 임시 독립 폴더로 복사해 `python -m pytest -q test_api.py`를 실행했습니다. 수정 검증은 다른 임시 폴더에서 solution.py를 main.py로 복사하여 **같은 테스트**를 실행했습니다. 원본 학생 시작 main.py는 유지했습니다. pytest 외부 플러그인은 비활성화하여 제공 검사만 확인했습니다.

추가로 시작·정답 각각 Uvicorn을 worker=1로 실행하여 실제 loopback HTTP로 /docs, /openapi.json 및 아래 입력을 요청했습니다. 충돌 방지를 위해 검증용 임시 포트를 사용했으며 학생 명령의 8000 포트와 동작은 같습니다. TestClient 검증과 실제 서버 검증을 구분합니다.

## 시작 코드 — 의도한 결함 재현

종료 코드: 1 (assertion 실패로 1이 예상됨)

```text
F.......F                                                                [100%]
=================================== FAILURES ===================================
________________________ test_valid_quantity[params0-1] ________________________

params = {}, qty = 1

    @pytest.mark.parametrize("params, qty", [({}, 1), ({"qty": 1}, 1), ({"qty": 5}, 5)])
    def test_valid_quantity(params, qty):
        response = client.get("/items/1", params=params)
        assert response.status_code == 200
>       assert response.json() == {"item_id": 1, "qty": qty, "total": qty * 1000}
E       AssertionError: assert {'item_id': 1...'total': 2000} == {'item_id': 1...'total': 1000}
E         
E         Omitting 1 identical items, use -vv to show
E         Differing items:
E         {'qty': 2} != {'qty': 1}
E         {'total': 2000} != {'total': 1000}
E         Use -v to get more diff

test_api.py:12: AssertionError
_________________________ test_document_default[qty-1] _________________________

field = 'qty', default = 1

    @pytest.mark.parametrize("field, default", [("qty", 1)])
    def test_document_default(field, default):
        schema = client.get("/openapi.json").json()
        parameters = schema["paths"]["/items/{item_id}"]["get"]["parameters"]
        parameter = next(p for p in parameters if p["name"] == field)
        assert parameter["in"] == "query"
        assert parameter["required"] is False
>       assert parameter["schema"]["default"] == default
E       assert 2 == 1

test_api.py:33: AssertionError
=============================== warnings summary ===============================
../../root/.local/lib/python3.12/site-packages/starlette/testclient.py:37
  /root/.local/lib/python3.12/site-packages/starlette/testclient.py:37: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED test_api.py::test_valid_quantity[params0-1] - AssertionError: assert {...
FAILED test_api.py::test_document_default[qty-1] - assert 2 == 1
2 failed, 7 passed, 1 warning in 0.29s
```

## 수정 코드 — 동일 검사

종료 코드: 0 (전체 통과 0)

```text
.........                                                                [100%]
=============================== warnings summary ===============================
../../root/.local/lib/python3.12/site-packages/starlette/testclient.py:37
  /root/.local/lib/python3.12/site-packages/starlette/testclient.py:37: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
9 passed, 1 warning in 0.28s
```

## 실제 HTTP 요청 결과 — 시작 코드

```json
{
  "transport": "real Uvicorn / HTTP, loopback temporary port, workers=1",
  "requests": [
    {
      "method": "GET",
      "path": "/docs",
      "input": null,
      "status": 200,
      "body": {
        "html_has_swagger_ui": true
      }
    },
    {
      "method": "GET",
      "path": "/openapi.json",
      "input": null,
      "status": 200,
      "body": {
        "openapi": "3.1.0",
        "paths": [
          "/items/{item_id}"
        ]
      }
    },
    {
      "method": "GET",
      "path": "/items/1",
      "input": null,
      "status": 200,
      "body": {
        "item_id": 1,
        "qty": 2,
        "total": 2000
      }
    },
    {
      "method": "GET",
      "path": "/items/1?qty=0",
      "input": null,
      "status": 422,
      "body": {
        "detail": [
          {
            "type": "greater_than_equal",
            "loc": [
              "query",
              "qty"
            ],
            "msg": "Input should be greater than or equal to 1",
            "input": "0",
            "ctx": {
              "ge": 1
            }
          }
        ]
      }
    }
  ]
}
```

## 실제 HTTP 요청 결과 — 수정 코드

```json
{
  "transport": "real Uvicorn / HTTP, loopback temporary port, workers=1",
  "requests": [
    {
      "method": "GET",
      "path": "/docs",
      "input": null,
      "status": 200,
      "body": {
        "html_has_swagger_ui": true
      }
    },
    {
      "method": "GET",
      "path": "/openapi.json",
      "input": null,
      "status": 200,
      "body": {
        "openapi": "3.1.0",
        "paths": [
          "/items/{item_id}"
        ]
      }
    },
    {
      "method": "GET",
      "path": "/items/1",
      "input": null,
      "status": 200,
      "body": {
        "item_id": 1,
        "qty": 1,
        "total": 1000
      }
    },
    {
      "method": "GET",
      "path": "/items/1?qty=0",
      "input": null,
      "status": 422,
      "body": {
        "detail": [
          {
            "type": "greater_than_equal",
            "loc": [
              "query",
              "qty"
            ],
            "msg": "Input should be greater than or equal to 1",
            "input": "0",
            "ctx": {
              "ge": 1
            }
          }
        ]
      }
    }
  ]
}
```

## 범위 감사와 수동 의미 검토

lesson_scope.json은 강사용 자료입니다. 모든 배포 파일의 현재 목적·실행 주체와 main/solution의 직접 선언 경로별 실제 TestClient 호출 인용을 등록했습니다. 정답은 main.py로 복사하여 같은 호출을 수행했습니다. 정적 범위 감사 결과는 아래에 기록합니다.

MANIFEST_AUDIT_RESULT

수동 확인: 경로의 변수 치환까지 따라 실제 호출을 확인했습니다. import·지역변수·모델·보조 함수·의존성은 현재 입력 처리 또는 검사에 사용합니다. 현재 차시에 실행되지 않는 미래 기능·health·통합 모의 서버는 없고, 시작 코드의 결함은 실제 실패로 재현했습니다. 정답의 불필요 분기·fallback을 남기지 않았습니다. 문서의 전체 코드와 실제 Python 파일을 대조했습니다. 정적 검사는 의미적 미사용 코드의 완전한 증명이 아닙니다.

## 미검증 한계

Swagger HTML과 명세의 HTTP 응답은 확인했지만 브라우저에서 CDN 자산 로딩·화면 렌더링·Try it out 클릭은 자동 실행하지 않았습니다. 학생/강사가 README 활동으로 확인합니다. Windows CMD 자체와 다른 Python 버전, 운영 DB·인증·성능·동시성·다중 worker는 검증하지 않았습니다. 외부 AI 서비스 호출은 수행하지 않았고 제공 프롬프트로 학생이 생성·검토합니다. 통과는 제공 계약과 사례 범위의 근거입니다.

## 제작 환경의 의존성 알림

실행 로그의 DeprecationWarning은 하위 라이브러리 Starlette가 AnyIO의 이전 BlockingPortal 별칭을 참조하는 알림입니다. 현재 검사의 실패 원인은 아니며 숨기지 않고 원문을 남겼습니다. 하위 패키지는 잠그지 않았으므로 설치 시점에 따라 이 알림의 유무가 달라질 수 있습니다.

제작 시 하위 패키지 관찰값: starlette=0.46.2, anyio=4.15.1, pydantic-core=2.33.2.
