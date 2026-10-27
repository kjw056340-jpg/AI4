# 강사용 지도·평가

## 의도한 재현과 정답

- `python check.py main`: 초기 GET 200, 등록 POST 201, ID `[1,3,3]` 출력 후 AssertionError (예상된 실패).
- `python check.py solution`: 같은 응답 상태에서 ID `[1,3,4]` 및 PASS.
- 정답의 유일한 필수 변경은 `return max(task["id"] for task in tasks) + 1`.
- `main.py`를 직접 수정했다면 반드시 학생 코드로 `python check.py main`을 다시 실행하도록 지도.

## 확인 질문 (학생)

1. `@app.get`가 선언되면 조회 함수가 즉시 실행되나요?
2. 목록 길이가 2이면 다음 ID도 무조건 3인가요?
3. `check.py`는 왜 별도의 Uvicorn 서버 없이 실행될까요?

## 강사용 답

1. 아니요. 등록만 되고 HTTP GET 요청에서 실행됩니다.
2. 아니요. 초기 최대 ID 3이므로 이 사례의 다음 ID는 4입니다.
3. TestClient가 FastAPI 앱을 프로세스 내부에서 요청 호출하기 때문입니다.

## 흔한 막힘

- `ModuleNotFoundError`: 가상환경과 requirements 설치 확인.
- `Address already in use`: 다른 서버 종료 또는 포트 확인.
- 브라우저에서 코드 수정이 반영되지 않음: 자동 재시작을 쓰지 않으므로 Ctrl+C 후 재실행.
- `check.py`를 여러 번 반복하면? 명령마다 새 Python 프로세스라 초기 데이터로 다시 시작.
- 빈 title: FastAPI 검증 오류 422이며, ID 중복 버그와 구분.

## 평가 (총 10점)

| 기준 | 점수 |
| --- | ---: |
| GET/POST 요청과 응답 해석 | 2 |
| 실패 재현 및 ID 중복 원인 설명 | 3 |
| 최소 수정 후 정상 재실행 | 3 |
| AI 조언 검증 및 제한점 설명 | 2 |

선택 심화는 기본 차시에 포함하지 않는다. 다음 시간에는 개별 항목 조회와 404를 다룬다.
