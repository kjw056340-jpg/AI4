# 4차시 제작 실행 검증

검증일: 2026-10-23 (한국 기준). Python 3.12.14 · Linux 실행 환경. 패키지는 requirements.txt에 기록했습니다. 학생 Windows CMD와 브라우저 수동 확인은 README 명령으로 재검증해야 합니다.

## 검증 방식

배포 시작 파일을 임시 독립 폴더로 복사해 `python -m pytest -q test_api.py`를 실행했습니다. 수정 검증은 다른 임시 폴더에서 solution.py를 main.py로 복사하여 **같은 테스트**를 실행했습니다. 원본 학생 시작 main.py는 유지했습니다. pytest 외부 플러그인은 비활성화하여 제공 검사만 확인했습니다.

추가로 시작·정답 각각 Uvicorn을 worker=1로 실행하여 실제 loopback HTTP로 /docs, /openapi.json 및 아래 입력을 요청했습니다. 충돌 방지를 위해 검증용 임시 포트를 사용했으며 학생 명령의 8000 포트와 동작은 같습니다. TestClient 검증과 실제 서버 검증을 구분합니다.

## 시작 코드 — 의도한 결함 재현

종료 코드: 1 (assertion 실패로 1이 예상됨)

```text
...F.......                                                              [100%]
=================================== FAILURES ===================================
_________________________ test_quote[10000-1000-9000] __________________________

amount = 10000, discount = 1000, payable = 9000

    @pytest.mark.parametrize("amount, discount, payable", [
        (1, 0, 1), (5000, 0, 5000), (9999, 0, 9999),
        (10000, 1000, 9000), (10001, 1000, 9001),
        (20000, 1000, 19000), (100000, 1000, 99000),
    ])
    def test_quote(amount, discount, payable):
        response = client.post("/quotes", json={"amount": amount})
        assert response.status_code == 200
>       assert response.json() == {"amount": amount, "discount": discount, "payable": payable}
E       AssertionError: assert {'amount': 10...yable': 10000} == {'amount': 10...ayable': 9000}
E         
E         Omitting 1 identical items, use -vv to show
E         Differing items:
E         {'payable': 10000} != {'payable': 9000}
E         {'discount': 0} != {'discount': 1000}
E         Use -v to get more diff

test_api.py:16: AssertionError
=============================== warnings summary ===============================
../../root/.local/lib/python3.12/site-packages/starlette/testclient.py:37
  /root/.local/lib/python3.12/site-packages/starlette/testclient.py:37: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED test_api.py::test_quote[10000-1000-9000] - AssertionError: assert {'am...
1 failed, 10 passed, 1 warning in 0.30s
```

## 수정 코드 — 동일 검사

종료 코드: 0 (전체 통과 0)

```text
...........                                                              [100%]
=============================== warnings summary ===============================
../../root/.local/lib/python3.12/site-packages/starlette/testclient.py:37
  /root/.local/lib/python3.12/site-packages/starlette/testclient.py:37: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
11 passed, 1 warning in 0.27s
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
          "/quotes"
        ]
      }
    },
    {
      "method": "POST",
      "path": "/quotes",
      "input": {
        "amount": 10000
      },
      "status": 200,
      "body": {
        "amount": 10000,
        "discount": 0,
        "payable": 10000
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
          "/quotes"
        ]
      }
    },
    {
      "method": "POST",
      "path": "/quotes",
      "input": {
        "amount": 10000
      },
      "status": 200,
      "body": {
        "amount": 10000,
        "discount": 1000,
        "payable": 9000
      }
    }
  ]
}
```

## 범위 감사와 수동 의미 검토

lesson_scope.json은 강사용 자료입니다. 모든 배포 파일의 현재 목적·실행 주체와 main/solution의 직접 선언 경로별 실제 TestClient 호출 인용을 등록했습니다. 정답은 main.py로 복사하여 같은 호출을 수행했습니다. 정적 범위 감사 결과는 아래에 기록합니다.

```text
PASS: 파일·API 명세 일치 및 정적 후보 검사 통과
필수 수동 확인: 근거가 실제 호출인지, 동적 경로·미사용 지역변수·의존성·차시간 혼입 여부.
이 검사는 실행 검증이나 의미적 사용 여부의 완전한 증명이 아닙니다.
```

수동 확인: 경로의 변수 치환까지 따라 실제 호출을 확인했습니다. import·지역변수·모델·보조 함수·의존성은 현재 입력 처리 또는 검사에 사용합니다. 현재 차시에 실행되지 않는 미래 기능·health·통합 모의 서버는 없고, 시작 코드의 결함은 실제 실패로 재현했습니다. 정답의 불필요 분기·fallback을 남기지 않았습니다. 문서의 전체 코드와 실제 Python 파일을 대조했습니다. 정적 검사는 의미적 미사용 코드의 완전한 증명이 아닙니다.

## 미검증 한계

Swagger HTML과 명세의 HTTP 응답은 확인했지만 브라우저에서 CDN 자산 로딩·화면 렌더링·Try it out 클릭은 자동 실행하지 않았습니다. 학생/강사가 README 활동으로 확인합니다. Windows CMD 자체와 다른 Python 버전, 운영 DB·인증·성능·동시성·다중 worker는 검증하지 않았습니다. 외부 AI 서비스 호출은 수행하지 않았고 제공 프롬프트로 학생이 생성·검토합니다. 통과는 제공 계약과 사례 범위의 근거입니다.

## 불충분한 초안의 실제 결과

시작 코드와 정답 모두 test_seed.py가 통과합니다. 경계 누락으로 시작 결함을 놓치는 사례입니다.

```text
..                                                                       [100%]
=============================== warnings summary ===============================
../../root/.local/lib/python3.12/site-packages/starlette/testclient.py:37
  /root/.local/lib/python3.12/site-packages/starlette/testclient.py:37: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2 passed, 1 warning in 0.26s
```

## 제작 환경의 의존성 알림

실행 로그의 DeprecationWarning은 하위 라이브러리 Starlette가 AnyIO의 이전 BlockingPortal 별칭을 참조하는 알림입니다. 현재 검사의 실패 원인은 아니며 숨기지 않고 원문을 남겼습니다. 하위 패키지는 잠그지 않았으므로 설치 시점에 따라 이 알림의 유무가 달라질 수 있습니다.

제작 시 하위 패키지 관찰값: starlette=0.46.2, anyio=4.15.1, pydantic-core=2.33.2.
