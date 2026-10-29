# Render 배포 가이드

현재 프로젝트는 **GitHub에 소스 업로드 → Supabase 준비 → Render Web Service 생성** 순서로 배포합니다. FastAPI가 화면과 API를 함께 제공하므로 프론트엔드를 따로 배포하지 않습니다.

로컬 서버에서 실제 Supabase 연결과 장바구니·모의 결제를 검증했습니다. 실제 Render 배포는 아직 진행하지 않았습니다. 기존 Supabase 프로젝트를 그대로 사용하면 DB를 새로 만들 필요가 없습니다.

## 1. Supabase 준비

1. Supabase에서 프로젝트를 만듭니다.
2. SQL Editor에서 [001_schema.sql](../sql/001_schema.sql) 전체를 실행합니다. 기존에 적용했다면 다시 실행하지 않습니다.
3. [002_seed.sql](../sql/002_seed.sql)을 실행해 샘플 상품을 추가합니다.
4. 프로젝트 URL과 서버 전용 **Secret key (`sb_secret_...`)**를 확인합니다. 기존 legacy service_role 키도 현재 코드에서 지원합니다.

현재 연결된 프로젝트는 이미 테이블과 상품 데이터가 준비되어 있으므로 1~3번을 다시 실행하지 않아도 됩니다.

이 프로젝트는 자체 users 테이블로 로그인합니다. Supabase Authentication 화면에서 사용자를 미리 등록할 필요는 없습니다. 서버 키는 Render 환경변수에만 입력하며 브라우저나 GitHub에 공개하지 않습니다. [Supabase API 키 공식 안내](https://supabase.com/docs/guides/getting-started/api-keys)

## 2. GitHub에 프로젝트 업로드

GitHub 저장소를 만들고 이 프로젝트의 소스를 업로드합니다. VSCode의 소스 제어 기능을 사용해도 됩니다.

`app/`, `templates/`, `static/`, `sql/`, `requirements.txt`, `render.yaml`이 포함되어야 합니다. `.env`, `.venv/`, 비밀키는 업로드하지 않습니다. 프로젝트의 `.gitignore`에 제외 규칙이 있습니다.

## 3. Render Web Service 생성

[Render 대시보드](https://dashboard.render.com/)에서 **New → Web Service**를 선택하고 GitHub 저장소를 연결합니다.

| 설정 | 입력값 |
| --- | --- |
| Name | 원하는 서비스명, 예: `ondo-shop` |
| Language / Runtime | Python 3 |
| Branch | 배포할 소스가 있는 브랜치 |
| Root Directory | requirements.txt가 저장소 최상위에 있으면 비워 둠. 하위 폴더에 있으면 그 폴더 경로 입력 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --no-proxy-headers` |
| Health Check Path | `/health` |

`$PORT`는 Render에서 설정하는 서버 포트이므로 그대로 입력합니다. 로컬 미리보기용 `tests.preview:preview`가 아닌 **app.main:app**으로 실행해야 합니다. 로그인 요청 제한기가 단일 프로세스 기준이므로 worker는 1개로 유지합니다. [Render FastAPI 공식 안내](https://render.com/docs/deploy-fastapi)

## 4. 환경변수 설정

서비스의 **Environment**에 아래 값을 입력합니다. 환경변수 값에는 따옴표를 붙이지 않습니다.

| 변수 | 값 |
| --- | --- |
| `PYTHON_VERSION` | `3.12.8` — 현재 render.yaml과 동일한 버전 |
| `SUPABASE_URL` | Supabase 프로젝트 주소, 예: `https://PROJECT_ID.supabase.co` |
| `SUPABASE_KEY` | 서버 전용 Secret key 또는 legacy service_role 키 |
| `JWT_SECRET` | 무작위로 생성한 32자 이상의 비밀키 |
| `APP_ORIGIN` | 실제 Render 서비스 주소, 예: `https://ondo-shop-xxxx.onrender.com` |
| `COOKIE_SECURE` | `true` |
| `ACCESS_TOKEN_MINUTES` | `120` — 선택, 생략해도 120분 |

JWT 비밀키는 로컬 프로젝트 터미널에서 다음과 같이 생성할 수 있습니다. 생성 결과를 JWT_SECRET에 입력합니다.

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

`APP_ORIGIN`에는 `/products` 같은 경로나 마지막 `/` 없이 사이트 주소만 입력합니다. 위 예시 주소를 그대로 사용하지 말고 **Render에서 실제로 배정한 주소**를 사용합니다. 서비스 생성 후에 주소를 확인했다면 APP_ORIGIN을 수정하고 **Save and deploy**로 적용합니다.

프로젝트의 `render.yaml`로 Blueprint를 생성하는 방법도 있습니다. 이 경우 빌드·시작 명령과 Secure 쿠키 설정이 포함되어 있고 JWT_SECRET은 자동 생성되지만, Supabase 값과 APP_ORIGIN은 직접 설정해야 합니다. 일반 Web Service 생성 시에는 위 표를 직접 입력합니다. [Render 환경변수 공식 안내](https://render.com/docs/configure-environment-variables)

## 5. 배포 및 확인

1. **Create Web Service / Deploy**를 실행합니다.
2. Logs에서 Python 패키지 설치 및 Uvicorn 시작 여부를 확인합니다.
3. 서비스 주소 뒤에 `/products`를 붙여 상품목록을 엽니다.
4. 회원가입 → 로그인 → 장바구니 → 주문 확정 → 모의 결제 → 구매내역을 확인합니다.
5. 로그아웃 후 `/account`에 접근하면 로그인 화면으로 이동하는지 확인합니다.

`/health`의 `{"status":"ok"}`는 서버 프로세스가 실행 중이라는 뜻입니다. DB 연결 성공까지 확인하는 것은 아니므로 상품목록과 회원가입도 별도로 확인합니다.

## 자주 발생하는 문제

| 증상 | 확인할 내용 |
| --- | --- |
| `Could not import module app.main` | Root Directory 아래에 app/main.py가 있는지 확인 |
| 필수 설정 누락으로 서버 시작 실패 | SUPABASE_URL, SUPABASE_KEY, JWT_SECRET 확인 |
| 상품 조회·회원가입에서 DB 오류 | SQL 적용 여부, 프로젝트 URL, 서버 키, Supabase 프로젝트 상태 확인 |
| 로그인·주문 요청에서 보안 확인 실패 | 브라우저 접속 주소와 APP_ORIGIN 일치 여부, 환경변수 적용 후 재배포 여부 확인 |
| 로그인 쿠키가 유지되지 않음 | HTTPS 주소로 접속했는지, COOKIE_SECURE=true인지 확인 |

도메인을 변경하면 APP_ORIGIN도 같은 주소로 바꾸고 재배포합니다. 결제는 모의 처리이며 실제 금액 청구와 배송은 제공하지 않습니다.

로컬에서 허용하는 localhost/127.0.0.1 별칭은 운영 환경에 적용되지 않습니다. Render의 APP_ORIGIN에는 실제 HTTPS 주소를 입력하고 COOKIE_SECURE=true를 유지합니다.
