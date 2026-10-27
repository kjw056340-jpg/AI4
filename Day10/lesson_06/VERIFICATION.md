# 실제 실행 검증·범위 감사

검증일: 2026-10-27 (한국 기준).
실제 환경: Linux, Python 3.12.14, SQLite 3.53.1.
외부 패키지 없이 실제 임시 파일 DB에서 실행했다.

## 수집한 출력

### python check.py main

```text
FAIL foreign_keys_enabled
PASS valid_message: rejected=False; violations=[]
FAIL missing_conversation: rejected=False; violations=[('messages', 2, 'conversations', 0)]
FAIL missing_user: rejected=False; violations=[('conversations', 20, 'users', 0)]
FAIL parent_conversation_delete: rejected=False; violations=[('messages', 1, 'conversations', 0)]
FAIL parent_user_delete: rejected=False; violations=[('conversations', 10, 'users', 0)]
PASS invalid_role: rejected=True; violations=[]
PASS null_content: rejected=True; violations=[]
RESULT failures=5
EXIT=1
```

### python check.py solution

```text
PASS foreign_keys_enabled
PASS valid_message: rejected=False; violations=[]
PASS missing_conversation: rejected=True; violations=[]
PASS missing_user: rejected=True; violations=[]
PASS parent_conversation_delete: rejected=True; violations=[]
PASS parent_user_delete: rejected=True; violations=[]
PASS invalid_role: rejected=True; violations=[]
PASS null_content: rejected=True; violations=[]
RESULT failures=0
EXIT=0
```

### python main.py

```text
외래키 설정: 0
문제: 없는 대화방의 메시지가 저장되었습니다.
EXIT=0
```

### python solution.py

```text
외래키 설정: 1
없는 대화방 거절: FOREIGN KEY constraint failed
EXIT=0
```

### python check.py main — 최소 수정 적용 후

```text
PASS foreign_keys_enabled
PASS valid_message: rejected=False; violations=[]
PASS missing_conversation: rejected=True; violations=[]
PASS missing_user: rejected=True; violations=[]
PASS parent_conversation_delete: rejected=True; violations=[]
PASS parent_user_delete: rejected=True; violations=[]
PASS invalid_role: rejected=True; violations=[]
PASS null_content: rejected=True; violations=[]
RESULT failures=0
EXIT=0
```

### python main.py — 최소 수정 적용 후

```text
외래키 설정: 1
없는 대화방 거절: FOREIGN KEY constraint failed
EXIT=0
```

## 확인 결과

시작 main의 의도한 실패를 실제 재현했고 solution 및 최소 수정 후 main은 8개 검사를 통과했다.
최소 수정 코드와 solution의 차이가 없는지 대조했다. 실행 후 main.py는 시작 버그 상태로 복원했다.
정상·오류의 DB 상태와 출력·설정·참조 또는 조회 결과를 각 check.py 계약으로 비교했다.

## 코드 범위 감사

스킬 audit_lesson_scope.py를 이 lesson 폴더에 실행해 종료 코드 0을 확인했다.
README의 전체 Python 코드와 main.py·check.py가 일치하는지 확인했다.
선언된 HTTP API가 없으므로 routes는 빈 배열이고 외부 의존성·모의 서버도 없다.
모든 함수와 SQL은 직접 실행 블록·check.py의 실제 호출로 연결된다.
각 표와 열은 현재 차시의 준비·예시 실행·검사에서 사용한다.
의도한 제약·조건·설정 누락은 실패 결과로 재현했다. 시작 코드의 결함을 미사용 코드 검사 통과로 정당화하지 않았다.
다른 lesson 파일을 import하지 않고 현재 표·목표에 필요한 코드만 제공했다.
표 정의 일부가 다음 차시에 반복되는 것은 각 차시가 독립 실행되기 위해서이며 통합 서버를 복사한 형태가 아니다.
정적 검사만으로 의미적 사용을 완전히 증명했다고 표현하지 않고 실행·수동 검토를 함께 수행했다.

## 검증 한계

Windows CMD에서는 실제 실행하지 않았다. 경로·명령·인자를 실제 파일과 대조했다.
독립된 Codex 세션 응답 품질을 별도로 시험한 것은 아니다. 프롬프트는 분석·수정·검토 활동 안내다.
다중 프로세스 동시 쓰기·인증·암호화·파일 접근 권한·실제 AI API는 검증하지 않았다.

## ZIP 검사

파일 목록·내부 경로·압축 무결성·필수 파일 존재와 캐시·가상환경·실제 DB·스킬 소스 제외를 확인했다.
