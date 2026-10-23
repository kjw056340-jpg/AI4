# 공식 근거와 검증 버전

확인일: 2026-10-23 (한국 기준). 아래 공식 문서를 열어 확인했습니다. 최신 문서와 설치 버전이 항상 같다고 가정하지 않고 실제 검사는 아래 버전으로 실행했습니다.

| 공식 문서 | URL | 관련 주제 |
| --- | --- | --- |
| FastAPI First Steps | https://fastapi.tiangolo.com/tutorial/first-steps/ | 1차시: /docs와 /openapi.json의 관계, 경로 등록 |
| FastAPI Query Validations | https://fastapi.tiangolo.com/tutorial/query-params-str-validations/ | 2차시: Annotated, Query, 기본값 |
| FastAPI Path Numeric Validations | https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/ | 2·5~8차시: Path의 ge 제약 |
| FastAPI Body Fields | https://fastapi.tiangolo.com/tutorial/body-fields/ | 3·4·7·8차시: 요청 모델 Field |
| Pydantic Fields | https://docs.pydantic.dev/latest/concepts/fields/ | 3·4·8차시: Field 범위와 strict |
| FastAPI Testing | https://fastapi.tiangolo.com/tutorial/testing/ | 전 차시: HTTPX 기반 TestClient와 pytest |
| pytest Parametrize | https://docs.pytest.org/en/stable/how-to/parametrize.html | 4차시 이후: 입력표를 여러 검사로 실행 |
| FastAPI Handling Errors | https://fastapi.tiangolo.com/tutorial/handling-errors/ | 5·6·7·8차시: HTTPException raise |
| FastAPI Response Model | https://fastapi.tiangolo.com/tutorial/response-model/ | 6차시: 응답 스키마·필터링 |
| pytest Fixtures | https://docs.pytest.org/en/stable/how-to/fixtures.html | 7·8차시: 테스트별 준비·정리 |

검증한 직접 의존성:

| 패키지 | 버전 |
| --- | --- |
| fastapi | 0.115.12 |
| pydantic | 2.11.5 |
| uvicorn | 0.34.2 |
| httpx | 0.28.1 |
| pytest | 8.3.5 |

기본값·범위·할인·상태 코드·좌석 정책은 이 수업의 업무 계약입니다. 공식 표준이 모든 API에 이 정책을 강제한다고 설명하지 않습니다.
