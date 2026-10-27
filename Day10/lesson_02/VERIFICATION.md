# 실제 실행 검증·범위 감사

검증일: 2026-10-27 (한국 기준).
실제 환경: Linux, Python 3.12.14, SQLite 3.53.1.
표준 라이브러리만 사용하고 실제 임시 .db 파일에서 실행했다.

## 수집한 출력

### python check.py main

```text
PASS seoul_two: expected=[3, 5], actual=[3, 5]
PASS seoul_one: expected=[3], actual=[3]
PASS seoul_all: expected=[3, 5, 1, 6], actual=[3, 5, 1, 6]
PASS busan: expected=[2], actual=[2]
PASS daejeon: expected=[4], actual=[4]
PASS no_match: expected=[], actual=[]
PASS sql_text_is_a_value: expected=[], actual=[]
FAIL zero_means_zero: expected=[], actual=[3, 5]
PASS negative_limit_rejected
PASS repeat_prepare_preserves_rows_and_quote
RESULT failures=1
EXIT=1
```

### python check.py solution

```text
PASS seoul_two: expected=[3, 5], actual=[3, 5]
PASS seoul_one: expected=[3], actual=[3]
PASS seoul_all: expected=[3, 5, 1, 6], actual=[3, 5, 1, 6]
PASS busan: expected=[2], actual=[2]
PASS daejeon: expected=[4], actual=[4]
PASS no_match: expected=[], actual=[]
PASS sql_text_is_a_value: expected=[], actual=[]
PASS zero_means_zero: expected=[], actual=[]
PASS negative_limit_rejected
PASS repeat_prepare_preserves_rows_and_quote
RESULT failures=0
EXIT=0
```

### python check.py main — 한 줄 수정 후

```text
PASS seoul_two: expected=[3, 5], actual=[3, 5]
PASS seoul_one: expected=[3], actual=[3]
PASS seoul_all: expected=[3, 5, 1, 6], actual=[3, 5, 1, 6]
PASS busan: expected=[2], actual=[2]
PASS daejeon: expected=[4], actual=[4]
PASS no_match: expected=[], actual=[]
PASS sql_text_is_a_value: expected=[], actual=[]
PASS zero_means_zero: expected=[], actual=[]
PASS negative_limit_rejected
PASS repeat_prepare_preserves_rows_and_quote
RESULT failures=0
EXIT=0
```

### python main.py --db [임시 파일] --city 서울 --limit 2

```text
[(3, '수아', '서울', 95), (5, '하린', '서울', 95)]
EXIT=0
```

### python main.py --db [임시 파일] --city 서울 --limit 0

```text
[(3, '수아', '서울', 95), (5, '하린', '서울', 95)]
EXIT=0
```

### python solution.py --db [임시 파일] --city 서울 --limit 0

```text
[]
EXIT=0
```

### python solution.py --db [임시 파일] --city 서울 --limit 1

```text
[(3, '수아', '서울', 95)]
EXIT=0
```

### python solution.py --db [임시 파일] --city 제주 --limit 2

```text
[]
EXIT=0
```

### python solution.py --db [임시 파일] --limit -1

```text
ValueError: limit은 0 이상이어야 합니다.
EXIT=1
```

## 확인한 동작

- 시작 main은 서울 0행 요청만 실패했다. 기본 도시 필터·정렬·일반 상한과 음수 거절은 유지됐다.
- 한 줄 수정 후 main과 solution은 10개 검사 모두 통과했다.
- CLI로 기본 상위 2행·0행·1행·없는 도시·음수 거절을 확인했다.
- 하나의 DB에 CLI 준비를 반복한 뒤 새 연결에서 행 수가 6개임을 확인했다.
- 따옴표가 있는 이름과 SQL처럼 보이는 도시 문자열이 값으로 전달됐다.
- main.py는 한 줄 수정 검증 후 오류 재현용 원본으로 복원했다.

## 코드 범위 감사

스킬의 audit_lesson_scope.py lesson_02를 실행해 종료 코드 0을 확인했다.

수동 의미 검토:

- prepare_database는 CLI·check.py에서 호출되며 여섯 행은 도시·정렬·상한·따옴표 검사에 쓰인다.
- executemany의 네 값, CREATE·INSERT OR IGNORE·commit·close는 실제 파일 준비에서 실행된다.
- find_users는 CLI와 각 입력 검사에서 normalize_limit을 호출한다. 정상 반환과 음수 ValueError를 실행했다.
- WHERE의 첫 ?와 LIMIT의 두 번째 ?에 city·effective_limit이 실제 순서대로 전달된다.
- 출력 열 네 개는 화면·검사에서 확인된다. 점수 동점 id 3·5와 낮은 점수 id 1·6 순서를 검증했다.
- argparse·Path·sqlite3·import_module·TemporaryDirectory import와 지역 변수는 현재 실습에 쓰인다.
- HTTP 경로·서버가 없으므로 routes는 빈 배열이다. 외부 의존성도 없다.
- 1차시 파일을 import하거나 다음 차시 UPDATE·DELETE·대화방·메시지 기능을 섞지 않았다.
- README의 전체 Python 코드와 실제 배포 파일, 명령·기대 결과를 대조했다.
- 모든 터미널 명령은 python을 사용하고 대상 소개·제작 상태 메타 문구를 제외했다.

정적 통과만으로 의미적 사용을 완전히 증명했다고 표현하지 않는다. 위 실제 실행과 수동 검토를 함께 수행했다.

## 검증 한계

실제 Windows CMD에서는 실행하지 않았다. 경로·명령은 파일과 대조했다.
Codex 프롬프트는 활동 안내이며 독립된 Codex 응답 품질 평가를 수행한 것은 아니다.
실습용 샘플 준비는 개인 DB의 데이터 정리·마이그레이션 기능이 아니다.
동시 쓰기·사용자 인증·다른 테이블 관계는 이번 조회 검증에서 다루지 않았다.

## 압축 검사

파일 목록·내부 경로·압축 무결성과 캐시·가상환경·DB 파일·스킬 소스 제외 여부를 확인했다.
