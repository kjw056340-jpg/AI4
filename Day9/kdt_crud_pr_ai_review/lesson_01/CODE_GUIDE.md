# 코드 읽기 가이드

1. `tasks`: GET 조회와 POST 등록이 함께 읽고 변경하는 메모리 목록. 서버 재시작 시 초기화.
2. `TaskCreate`: 요청 본문의 `title`이 비어 있지 않도록 검증. 빈 문자열은 FastAPI가 422로 응답 (현재 코드에서 실제로 `POST /tasks` 요청으로 확인 가능).
3. `next_id`: POST 호출 도중 실행되는 보조 함수. 의도된 버그는 목록 길이를 다음 ID로 오해한 부분.
4. `@app.get('/tasks')`: GET 경로 등록; 클라이언트가 요청할 때 `list_tasks` 실행.
5. `@app.post('/tasks')`: POST 경로 등록; 유효한 JSON을 보내면 `create_task`가 `next_id`를 실행한 뒤 리스트에 추가.
6. `check.py`: 모듈을 하나 선택해서 TestClient로 GET→POST→GET 순서의 실제 요청을 보냄. 모든 요청은 한 프로세스의 같은 `tasks`를 사용.

## 예상 → 관찰 → 원인 → 수정 → 검증

- 예상: `[1, 3]` 뒤에는 새 ID 4.
- 실제 시작 코드: `[1, 3, 3]`, 마지막 검사에서 AssertionError.
- 원인: `len(tasks) + 1`은 항목 수 기준이어서 ID 중간이 비어 있으면 중복 가능.
- 최소 수정: `max(task['id'] for task in tasks) + 1` (현재 차시는 초기 데이터가 비어 있지 않다는 전제).
- 정답 결과: `[1, 3, 4]`, PASS.

본 차시는 GET·POST 두 경로만 포함한다. PUT/PATCH/DELETE, 데이터베이스, 인증, GitHub API는 이번 차시에서 구현하지 않는다.
