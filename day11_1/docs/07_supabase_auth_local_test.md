# Supabase Auth 전환 및 배포 전 로컬 테스트

작성일: 2026-10-30. 프로젝트 위치: `C:\Users\Playdata\dev\day11_1`.

## 적용 내용

인증은 Supabase Auth의 이메일·비밀번호 로그인, 이메일 인증, 토큰 갱신, 전체 세션 로그아웃을 사용합니다. `public.users`는 회원 프로필·권한·주문 연결용입니다. 앱은 더 이상 회원 비밀번호를 해시하거나 자체 토큰만으로 로그인을 허용하지 않습니다.

서버가 Supabase `/auth/v1/user`로 사용자를 확인하고 `auth_user_id`로 쇼핑몰 회원을 연결합니다. Access/refresh token은 HttpOnly 쿠키에 보관하며 JavaScript나 localStorage에 전달하지 않습니다. 별도 서명 쿠키는 사용자·토큰·`token_version`을 묶어 로그아웃 직후의 기존 쿠키 재사용을 차단합니다. `JWT_SECRET`은 이 보조 쿠키의 서명키이며 Supabase JWT 키가 아닙니다. 쿠키 유효기간은 발급·갱신 후 7일이고 Access token 만료는 Supabase 설정을 따릅니다.

| 기능 | 비회원 | 일반 회원 | 관리자 |
|---|---|---|---|
| 판매 중 상품 목록·상세 | 허용 | 허용 | 허용 |
| 프로필·비밀번호 변경·회원 탈퇴 | 불가 | 본인만 | 본인만 |
| 장바구니 추가·변경·삭제 | 불가 | 본인만 | 본인만 |
| 주문 생성·조회·미결제 취소 | 불가 | 본인만 | 본인만 |
| 모의 결제·결제 내역 | 불가 | 본인만 | 본인만 |
| `/admin` 상품 등록·수정·재고·판매 여부 관리 | 불가 | 불가 | 허용 |
| `/admin` 전체 주문·배송 정보 조회 | 불가 | 불가 | 허용 |

다른 회원의 주문·결제는 404, 관리자 기능의 일반 회원 접근은 403, 미인증 API 접근은 401을 반환합니다. 금액·소유자·권한을 요청에 넣어 변경할 수 없습니다. 관리자가 일반 구매 API로 다른 회원의 주문을 취소하거나 결제할 수는 없습니다. 배송 상태·환불·실제 PG 연동은 현재 프로젝트 기능에 포함되어 있지 않습니다.

역할은 서버 전용 `users.role`에서 매 요청 읽습니다. 사용자가 수정 가능한 Auth `user_metadata`에는 권한을 맡기지 않습니다. DB는 기존처럼 RLS를 활성화하고 `anon`/`authenticated`의 쇼핑몰 테이블·RPC 직접 접근을 막습니다. 서버 전용 키로만 접근하며, API와 트랜잭션 함수가 소유권·계정 활성 상태를 검사합니다. 브라우저에서 Supabase DB에 직접 접근하는 방식의 RLS 정책은 아닙니다.

## 1. 환경 준비 — PowerShell

아래 명령은 프로젝트 폴더에서 실행합니다. 운영 DB 대신 테스트용 Supabase 프로젝트를 연결하세요. 앱 서버만 로컬에서 실행되고 Auth/DB는 지정한 Supabase 프로젝트에 연결됩니다.

```powershell
Set-Location C:\Users\Playdata\dev\day11_1
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

기존 `.venv`가 있으면 생성 명령은 생략할 수 있습니다. 마지막 명령으로 생성한 값을 `.env`의 `JWT_SECRET`에 설정합니다. `.env`를 다음과 같이 편집합니다. 기존 `.env`는 위 명령으로 덮어쓰지 않습니다.

```dotenv
SUPABASE_URL=https://YOUR_TEST_PROJECT.supabase.co
SUPABASE_KEY=YOUR_TEST_PROJECT_SERVER_SECRET_OR_SERVICE_ROLE_KEY
JWT_SECRET=GENERATED_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
APP_ORIGIN=http://127.0.0.1:8000
COOKIE_SECURE=false
```

`SUPABASE_KEY`는 secret 또는 legacy service_role 서버 키입니다. 브라우저·저장소에 노출하지 마세요. `ACCESS_TOKEN_MINUTES`는 더 이상 사용하지 않습니다.

## 2. DB 변경과 Supabase Auth 설정

DB 백업 후 **테스트 프로젝트의 Supabase SQL Editor**에서 적용합니다. 이 변경은 앱 시작 시 자동 실행되지 않습니다.

- 기존 쇼핑몰 DB: `sql/003_fix_payment_function.sql` 적용 여부를 확인한 다음 `sql/004_supabase_auth.sql` 실행.
- 새 테스트 DB: `sql/001_schema.sql` → `sql/002_seed.sql` → `sql/003_fix_payment_function.sql` → `sql/004_supabase_auth.sql` 순서로 실행.
- 최신 `004`는 반복 실행할 수 있습니다. 기존 컬럼과 회원·주문 데이터를 유지하고 함수·트리거를 갱신하며 API 스키마 캐시를 새로고침합니다. 기존 DB에 `001`을 다시 실행하지 마세요. `004` 이후에 이전 `003`을 재실행하지 마세요.

Authentication 설정에서 Email provider와 이메일 인증을 켭니다. Site URL은 `http://127.0.0.1:8000`, 허용 Redirect URL에는 `http://127.0.0.1:8000/login`을 추가합니다. 기본 확인 메일 링크를 누른 뒤 로컬 로그인 화면에서 로그인하세요. 앱은 링크의 토큰을 읽지 않으며, 가입 직후 세션이 없으면 이메일 확인 안내를 표시합니다. 이메일 인증을 끈 테스트 프로젝트에서는 가입 즉시 로그인됩니다.

설정 확인 SQL:

```sql
select column_name from information_schema.columns
where table_schema='public' and table_name='users'
  and column_name in ('auth_user_id','role');

select relname, relrowsecurity from pg_class
where oid in ('public.users'::regclass,'public.orders'::regclass,
              'public.order_items'::regclass,'public.payments'::regclass);

select has_table_privilege('authenticated','public.users','UPDATE') as must_be_false,
       has_function_privilege('authenticated',
         'public.shop_mutate(uuid,integer,text,jsonb)','EXECUTE') as must_also_be_false;
```

## 3. 기존 회원 연결 — 주문 UUID 유지

### 로그인 시 '데이터를 처리하지 못했습니다'가 나오는 경우

2026-10-30 실제 연결 점검에서 DB 오류 `42703`과 `auth_user_id` 컬럼 누락을 확인했습니다. `004`가 적용되지 않은 상태에서 Auth 로그인 후 프로필을 조회하면 발생합니다.

1. Supabase 프로젝트의 SQL Editor에서 최신 `sql/004_supabase_auth.sql` 전체를 실행합니다. 이전 파일로 실행했을 때 `column "auth_user_id" already exists`가 나오면 편집기의 내용을 지우고 수정된 파일 전체를 다시 복사합니다. 최신 파일은 기존 컬럼이 있어도 실행할 수 있습니다.
2. `sql/005_sync_verified_auth_profiles.sql` 전체를 실행합니다. 이 SQL은 관리자가 실행하는 보정 절차이며, **Supabase가 이메일을 인증한 계정만** 같은 이메일의 기존 회원에 연결합니다. 트리거 설치 전 가입한 계정은 누락된 프로필을 생성합니다. 기존 회원 UUID·주문·권한은 유지하며, 비활성·미인증·삭제·익명 계정은 연결하지 않습니다. 반복 실행할 수 있습니다.
3. 로컬 로그인 화면을 새로고침하고 로그인합니다. 서버 재설치는 필요하지 않습니다.

이 보정 SQL은 아직 원격 DB에서 실행하지 않았습니다. 앱의 서버 키에는 SQL 스키마 변경 권한이 없으므로 SQL Editor에서 실행해야 합니다. 이메일 인증이 끝나지 않은 계정은 아래의 수동 연결 조건도 충족하지 않습니다.

기존 비밀번호를 Auth에 자동 복사하지 않습니다. 기존 회원은 **같은 이메일로 Auth 계정을 만들고 이메일을 인증한 뒤**, 관리자가 계정 소유를 확인하고 아래 SQL로 연결합니다. 기존 회원과 같은 이메일의 신규 Auth 가입에는 프로필을 자동 생성하거나 연결하지 않습니다. 연결 전 로그인은 401입니다. `users.id`를 바꾸지 않으므로 주문·결제의 FK가 유지됩니다.

```sql
-- 실제 확인한 쇼핑몰 회원 UUID와 Auth UUID로 교체하세요.
update public.users u
set auth_user_id=a.id, token_version=u.token_version+1, updated_at=now()
from auth.users a
where u.id='SHOP_USER_UUID'::uuid
  and a.id='VERIFIED_AUTH_USER_UUID'::uuid
  and u.auth_user_id is null and u.is_active
  and lower(a.email)=u.email and a.email_confirmed_at is not null
returning u.id,u.email,u.auth_user_id;
```

반환이 1행인지 확인합니다. 자동으로 일치하지 않는 계정은 연결하지 말고 이메일·소유자를 확인하세요. 신규 Auth 가입은 트리거가 일반 회원 프로필을 생성합니다. 마이그레이션 전부터 Auth 계정이 있던 경우도 별도 연결 확인이 필요합니다.

연결과 로그인·기존 구매 내역 확인이 끝난 회원의 이전 비밀번호 해시를 제거합니다.

```sql
update public.users set password_hash=null
where auth_user_id is not null and password_hash is not null;
```

## 4. 관리자 계정 준비

일반 회원 계정을 가입·인증한 뒤, SQL Editor에서 **확인한 해당 계정만** 관리자로 지정합니다.

```sql
update public.users set role='admin'
where auth_user_id='VERIFIED_ADMIN_AUTH_UUID'::uuid and is_active
returning id,email,role;
```

다음 요청부터 관리자 권한이 적용됩니다. `role='member'`로 수정하면 같은 로그인 세션에서도 즉시 관리자 권한이 사라집니다. 앱에서 사용자가 자신의 역할을 수정하는 API는 제공하지 않습니다.

## 5. 로컬 실행

```powershell
Set-Location C:\Users\Playdata\dev\day11_1
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

접속: [상품목록](http://127.0.0.1:8000/products), [회원가입](http://127.0.0.1:8000/register), [로그인](http://127.0.0.1:8000/login), [관리자](http://127.0.0.1:8000/admin), [API 명세](http://127.0.0.1:8000/api/docs). 종료는 실행 터미널에서 `Ctrl+C`입니다.

`tests.preview:preview`는 실제 Supabase 검증용이 아닙니다. 실제 테스트에는 위의 `app.main:app`을 사용하세요. 로컬 주소는 `127.0.0.1`로 통일하면 쿠키 혼동을 줄일 수 있습니다.

## 6. 자동 테스트 — 별도 터미널

Auth/DB 대역을 쓰는 자동 테스트는 원격 DB를 수정하지 않습니다.

```powershell
Set-Location C:\Users\Playdata\dev\day11_1
.\.venv\Scripts\python.exe -m pytest -q -m "not postgres"
```

포함: Supabase Auth 호출 형식·오류 처리, 이메일 확인 대기, 토큰 갱신, 만료된 화면 세션 복구, 로그아웃·비밀번호 변경 후 전체 이전 쿠키 재사용 차단, 비활성 회원, 관리자 권한 회수, 권한 주입 차단, 기존 소유권 검사, CSRF, SQL 구문 검사.

실제 PostgreSQL 트랜잭션 테스트는 **001~004를 적용한 테스트 전용 DB**에만 실행합니다. 명령 실행 전 테스트 DB 연결 문자열을 준비하세요. 이 테스트는 Auth 로그인 자체를 검증하지 않으며, 동시성 테스트는 테스트 행을 커밋한 뒤 정리합니다.

```powershell
$env:TEST_DATABASE_URL = Read-Host '테스트 전용 PostgreSQL 연결 문자열'
.\.venv\Scripts\python.exe -m pytest -q -m postgres
Remove-Item Env:TEST_DATABASE_URL
```

## 7. 실제 Supabase Auth + 로컬 API 검증

일반 회원 A, 일반 회원 B, 관리자 계정을 각각 가입·이메일 인증합니다. 회원 B로 상품을 주문하고 모의 결제까지 완료한 뒤 실행합니다. 아래 이메일을 실제 테스트 계정으로 바꿉니다. 비밀번호는 화면에 표시하지 않는 입력창으로 받으며 토큰도 출력하지 않습니다.

```powershell
.\.venv\Scripts\python.exe scripts/smoke_auth.py --member-email member-a@example.com --other-email member-b@example.com --admin-email admin@example.com
```

이 명령은 기존 테스트 계정으로 로그인하고 회원 B의 최신 주문·결제에 A가 접근할 수 없는지 검사합니다. A의 타인 주문 취소·결제 요청도 404여야 합니다. 마지막에 테스트 계정들을 전체 세션 로그아웃하므로 해당 계정으로 열린 브라우저에서도 다시 로그인해야 합니다. 관리자 검사를 생략하려면 `--admin-email`을 빼세요. 실패하면 `PASS`가 끝난 바로 다음 단계의 상태 코드를 확인합니다.

## 8. 브라우저 확인표

- [ ] 비회원: 상품 조회 가능, 장바구니·주문·마이페이지는 로그인으로 이동.
- [ ] 가입: 이메일 확인이 켜져 있으면 확인 안내 후 로그인 화면으로 이동, 인증 후 로그인 성공.
- [ ] 회원 A: 장바구니 수량 변경·삭제, 주문 생성·미결제 취소, 모의 결제·구매 내역 정상.
- [ ] 회원 B: A의 장바구니·주문·결제·배송지가 보이지 않음.
- [ ] 회원 A: `/admin` 직접 접속 403, 관리자 메뉴 숨김.
- [ ] 관리자: 관리자 메뉴 표시, 상품 등록·수정·재고·판매 여부 변경, 전체 주문 조회 가능.
- [ ] 권한 회수: SQL로 `member`로 변경 후 같은 세션에서 관리자 화면·API 403.
- [ ] 비밀번호 변경: 현재 비밀번호가 틀리면 거부, 성공하면 새 비밀번호 로그인 가능, 기존 다른 브라우저 세션은 거부.
- [ ] 로그아웃: 뒤로 가기·새로고침·다른 탭에서도 보호 API 거부.
- [ ] 토큰 만료: 테스트 Auth의 JWT 만료 시간을 줄인 후 기다렸다가 마이페이지 새로고침. refresh token이 유효하면 로그인 유지. 다른 설정값은 테스트 후 복원.
- [ ] 탈퇴: 비밀번호 확인 후 회원·배송 개인정보 익명화, 미결제 주문 취소, 결제 내역 보존, 재로그인 거부, Auth 계정 soft deletion 확인.

탈퇴는 쇼핑몰 DB와 Auth API의 두 작업이므로 원격 장애 중 완전한 단일 트랜잭션이 될 수 없습니다. DB 비활성화 후 Auth 정리가 실패하면 503 안내를 표시하고 모든 쇼핑몰 접근을 차단합니다. 관리자는 남아 있는 `auth_user_id`를 확인하여 Supabase Auth 관리자 기능으로 soft deletion을 재시도해야 합니다. soft deletion 전에는 Auth 쪽에 개인정보가 남을 수 있습니다.

## 9. 이번 작업에서의 확인 결과와 피드백

로컬 검증 결과: **64개 통과, 실제 PostgreSQL 테스트 7개 생략**(`TEST_DATABASE_URL` 미설정). SQL 구문 검사, JavaScript 구문 검사와 Python 컴파일 검사도 통과했습니다. 실제 Supabase SQL 적용·메일 전송·브라우저 구매·배포는 아직 실행하지 않았습니다. 위 2~8단계로 테스트 환경에서 확인한 후 배포 여부를 판단합니다.

테스트 후 아래 내용을 채워 채팅으로 전달해 주세요. 비밀번호·API 키·쿠키·토큰은 보내지 마세요.

```text
테스트 일시:
신규 계정 / 기존 회원 연결:
회원가입·이메일 확인·로그인·로그아웃: 성공 / 실패
장바구니·주문·모의 결제: 성공 / 실패
회원 A/B 소유권 검사: 성공 / 실패
관리자 상품·전체 주문·권한 회수: 성공 / 실패
비밀번호 변경·탈퇴·토큰 갱신: 성공 / 실패
실패한 화면 주소와 동작:
응답 상태 코드와 화면 메시지:
원하는 수정 사항:
```

참고한 공식 문서: [Supabase Auth API 명세](https://github.com/supabase/auth/blob/master/openapi.yaml), [서버 인증 가이드](https://supabase.com/docs/guides/auth/server-side/advanced-guide), [사용자 관리](https://supabase.com/docs/guides/auth/managing-user-data), [Auth 관리자 삭제](https://supabase.com/docs/reference/python/auth-admin-deleteuser).
