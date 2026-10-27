# 실행 검증과 범위 감사

검증일: 2026-10-27 (한국 기준).
실제 환경: Linux, Python 3.12.14, SQLite 3.53.1.
Python 표준 라이브러리만 사용했다. 메모리 DB로 대체하지 않고 실제 임시 .db 파일에서 검증했다.

## 실제 실행 결과

### python check.py main

```text
INSIDE: [(1, '민지')]
REOPENED: []
SECOND REOPENED: []
PASS visible_before_close
FAIL saved_after_reconnect
PASS quote_in_name_preserved
FAIL both_rows_saved
PASS null_rejected
PASS existing_rows_preserved_on_error
RESULT failures=2
EXIT=1
```

### python check.py solution

```text
INSIDE: [(1, '민지')]
REOPENED: [(1, '민지')]
SECOND REOPENED: [(1, '민지'), (2, "O'Neil")]
PASS visible_before_close
PASS saved_after_reconnect
PASS quote_in_name_preserved
PASS both_rows_saved
PASS null_rejected
PASS existing_rows_preserved_on_error
RESULT failures=0
EXIT=0
```

### python check.py main — 한 줄 수정 후

```text
INSIDE: [(1, '민지')]
REOPENED: [(1, '민지')]
SECOND REOPENED: [(1, '민지'), (2, "O'Neil")]
PASS visible_before_close
PASS saved_after_reconnect
PASS quote_in_name_preserved
PASS both_rows_saved
PASS null_rejected
PASS existing_rows_preserved_on_error
RESULT failures=0
EXIT=0
```

### python main.py --db [새 임시 DB 경로]

```text
연결 안에서: [(1, '민지')]
다시 연결하면: []
EXIT=0
```

### python solution.py --db [새 임시 DB 경로]

```text
연결 안에서: [(1, '민지')]
다시 연결하면: [(1, '민지')]
EXIT=0
```

### python solution.py --db [같은 파일 재실행]

```text
연결 안에서: [(1, '민지'), (2, '민지')]
다시 연결하면: [(1, '민지'), (2, '민지')]
EXIT=0
```

## 확인한 동작

- 시작 코드: 같은 연결에서는 민지가 보이지만 연결 종료 후에는 사용자 행이 남지 않았다.
- 최소 수정 후와 solution: 첫 사용자·두 번째 사용자가 새 연결에서도 유지됐다.
- 따옴표가 포함된 이름 O'Neil은 값 그대로 전달됐다.
- None은 NOT NULL에 거절됐고 실패 뒤에도 기존 행이 유지됐다.
- 독립 CLI 실행 후 다른 연결로 파일을 읽어 main은 0행, solution은 1행임을 확인했다.
- 같은 solution DB 파일로 재실행하면 같은 이름의 행이 하나 더 추가되는 동작을 확인했다.
- 검사에는 임시 디렉터리를 이용했고 배포 폴더에 개인 DB 파일을 만들지 않았다.
- main.py는 한 줄 수정 재검사 후 오류 재현용 원본으로 복원했다.

## 범위 감사

스킬의 scripts/audit_lesson_scope.py lesson_01에서 종료 코드 0을 확인했다.
배포 스크립트 자체는 실습 폴더에 넣지 않았다.

수동 의미 검토:

- save_user·read_users는 직접 실행 블록과 check.py에서 실제 호출된다.
- 연결 생성·CREATE·테이블 준비 commit·INSERT·SELECT·fetchall·finally close가 현재 실습 흐름에서 실행된다.
- main/solution 선택 두 분기, 값 튜플의 따옴표 입력, NOT NULL 오류·연결 종료를 실행 확인했다.
- --db를 지정한 CLI와 기본 DB 위치 계산을 코드와 문서에서 대조했다.
- argparse·Path·sqlite3·import_module·TemporaryDirectory와 지역 변수는 현재 실행·검증에 쓰인다.
- 직접 사용하는 외부 패키지·HTTP API·모의 서버는 없고 routes는 빈 목록이다.
- 대화방·메시지·FK 구현은 사용자 단일 테이블 실습에 섞지 않았다.
- 문서에 포함한 main.py·check.py 전체 코드와 실제 파일이 일치한다.
- 모든 배포 문서에서 대상 소개·기본 구성 소개·제작 상태 안내 문구를 검사해 제외했다.

정적 통과가 모든 사용 의미를 완전히 증명하는 것은 아니다. 실제 실행과 위 수동 검토를 함께 수행했다.

## 실행하지 않은 항목

Windows CMD 자체에서는 실행하지 않았으며 경로·인용·파일·명령은 문서와 대조했다.
Codex 프롬프트는 분석·수정·검토 활동 안내다. 독립 Codex 세션의 응답 품질을 별도 측정하지 않았다.
사용자 로그인 인증·파일 접근 통제·다중 프로세스 동시 쓰기·외래키 관계는 이 저장 검사에서 검증하지 않았다.

## ZIP 확인

배포 경로·필수 파일·압축 무결성을 검사하고 캐시·가상환경·실제 DB 파일·스킬 소스를 제외했다.
