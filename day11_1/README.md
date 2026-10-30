# 온도 쇼핑몰 — DB 설계 문서

회원·상품·장바구니/주문·결제의 관계와 구매 과정의 데이터 변화를 설명합니다.

## 실제 쇼핑몰 실행

**Supabase Auth 전환 후에는 [배포 전 로컬 테스트 안내](docs/07_supabase_auth_local_test.md)에 따라 `sql/004_supabase_auth.sql` 적용과 기존 회원 계정 연결을 먼저 진행하세요.** 로그인·로그아웃·토큰 갱신은 Supabase Auth를 사용하며, 일반 회원과 관리자의 권한을 구분합니다. 실행 명령·자동 테스트·실제 계정 검증·피드백 양식은 해당 문서에 정리했습니다.

Supabase 연결값을 `.env`에 설정한 후 프로젝트 터미널에서 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

[상품목록 열기](http://127.0.0.1:8000/products)

**장바구니·주문·결제는 `app.main:app`으로 실행해야 합니다.** `tests.preview:preview`는 화면만 확인하는 샘플 서버로 실제 DB에 장바구니를 저장하지 않습니다. 기존 샘플 서버가 실행 중이면 먼저 해당 터미널에서 Ctrl+C로 종료합니다. 샘플 서버에서 가입한 계정은 실제 DB에 없으므로 실제 서버에서 회원가입이 필요합니다.

## 읽는 순서

| 순서 | 문서 | 내용 |
| --- | --- | --- |
| 1 | [최소 ERD](erd.md) | 테이블 5개의 핵심 관계와 주문 상태 |
| 2 | [구매 시뮬레이션](purchase-simulation.md) | 머그 2개 구매 시 테이블별 생성·변경·조회 과정 |
| 3 | [테이블 정의서](table-definition.md) | 실제 SQL 기준 전체 컬럼·PK/FK·제약조건·인덱스 |

## ERD 보기

[erd.md](erd.md) 안에 `mermaid` 코드 블록을 넣었습니다. **VSCode에서 파일을 열고 Markdown 미리보기(`Ctrl+Shift+V`)**로 확인하세요. Mermaid를 지원하는 Markdown 뷰어에서는 관계도가 렌더링됩니다. 코드만 보이면 해당 뷰어에 Mermaid 지원이 필요합니다.

별도로 Mermaid 원본 [erd.mmd](erd.mmd)도 제공합니다. `.mmd` 파일 지원 미리보기에서는 원본을 바로 열 수 있습니다. Markdown의 Mermaid 코드와 원본 내용은 같습니다.

## 관련 파일

- [테이블·함수 생성 SQL](sql/001_schema.sql)
- [샘플 상품 INSERT SQL](sql/002_seed.sql)
- [상세 요구사항과 구현 가정](docs/01_design.md)
- [API 명세](docs/03_api.md)
- [Render 배포 가이드](docs/04_deployment.md)
- [실제 결제 검증 결과와 수정 안내](docs/05_payment_verification.md)

ERD는 핵심 컬럼만 표시하며, 테이블 정의서는 기존 SQL의 전체 컬럼을 설명합니다. 설명 문서는 모두 Markdown으로 작성했습니다. 실제 Supabase 검증 결과는 위 검증 문서를 참고하세요. Render 배포 검증은 아직 진행하지 않았습니다.
