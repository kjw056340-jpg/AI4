# API 명세

서버 실행 후 `/openapi.json`에서 정확한 JSON Schema를 확인할 수 있습니다. 프론트엔드와 API는 동일 출처입니다. 인증은 Supabase Auth의 access/refresh token과 세션 검증용 HttpOnly 쿠키를 사용합니다. 최신 설정·권한표는 [Supabase Auth 로컬 테스트 안내](07_supabase_auth_local_test.md)를 참고하세요.

| 메서드 | 경로 | 설명 | 인증 |
| --- | --- | --- | --- |
| GET | `/api/csrf` | CSRF 쿠키와 JSON 토큰 발급 | 불필요 |
| POST | `/api/auth/register` | Auth 회원가입 (201), 이메일 확인 대기 또는 자동 로그인 | 불필요 |
| POST | `/api/auth/login?next=...` | 로그인, 안전한 복귀 경로 반환 | 불필요 |
| POST | `/api/auth/logout` | 전체 기기 토큰 무효화, 쿠키 삭제 | 필요 |
| POST | `/api/auth/refresh` | refresh token·세션 쿠키 검증 후 토큰 교체 | 세션 쿠키 필요 |
| POST | `/api/admin/products` | 상품 등록 (201) | 관리자 |
| PUT | `/api/admin/products/{product_id}` | 상품 전체 정보·재고·판매 여부 수정 | 관리자 |
| GET | `/api/admin/orders?page=1` | 전체 회원 주문 조회, 10개씩 | 관리자 |
| GET | `/api/me` | 내 정보 조회 | 필요 |
| PATCH | `/api/me` | 이름·연락처·주소·비밀번호 수정 | 필요 |
| DELETE | `/api/me` | 비밀번호 확인 후 탈퇴 | 필요 |
| GET | `/api/products?category=리빙&page=1` | 공개 상품 목록, 12개씩 | 불필요 |
| GET | `/api/products/{product_id}` | 공개 상품 상세 | 불필요 |
| GET | `/api/cart` | 활성 장바구니, 없으면 빈 구조 | 필요 |
| POST | `/api/cart/items` | 상품 추가, 같은 상품은 수량 합산 | 필요 |
| PATCH | `/api/cart/items/{product_id}` | 상품 수량 설정 | 필요 |
| DELETE | `/api/cart/items/{product_id}` | 상품 삭제 | 필요 |
| POST | `/api/orders/checkout` | 주문 확정, 금액 재계산 (201) | 필요 |
| GET | `/api/orders?page=1` | 내 주문 목록, 10개씩, CART 제외 | 필요 |
| GET | `/api/orders/{order_id}` | 내 주문 및 결제 상세 | 필요 |
| POST | `/api/orders/{order_id}/cancel` | 결제 대기 주문 취소 | 필요 |
| POST | `/api/payments` | 모의 결제, 중복 요청에 기존 결과 | 필요 |
| GET | `/api/payments/{payment_id}` | 내 결제 이력 상세 | 필요 |
| GET | `/health` | 프로세스 상태, DB 연결은 검사하지 않음 | 불필요 |

## 요청 예시

모든 POST/PUT/PATCH/DELETE는 먼저 GET `/api/csrf`로 쿠키를 받은 후 응답의 csrf_token을 `X-CSRF-Token` 헤더로 보냅니다. 브라우저의 Origin이 있으면 APP_ORIGIN과 일치해야 합니다. API 호출에는 같은 cookie jar를 유지해야 합니다.

회원가입:

```json
{"email":"member@example.com","password":"my-password123","name":"홍길동","phone":"010-1234-5678","address":"서울시 예시로 123"}
```

로그인:

```json
{"email":"member@example.com","password":"my-password123"}
```

장바구니 추가:

```json
{"product_id":"10000000-0000-4000-8000-000000000001","quantity":2}
```

장바구니 주문:

```json
{"source":"cart","recipient":"홍길동","phone":"010-1234-5678","address":"서울시 예시로 123"}
```

바로 구매:

```json
{"source":"direct","product_id":"10000000-0000-4000-8000-000000000001","quantity":1,"recipient":"홍길동","phone":"010-1234-5678","address":"서울시 예시로 123"}
```

결제: order_id에는 checkout 응답의 id를, idempotency_key에는 새 UUID를 사용합니다. 네트워크 오류 재시도에는 같은 key와 order_id를 유지합니다. 금액은 보내지 않습니다. 서버가 확정 주문의 저장 금액으로 처리합니다.

```json
{"order_id":"20000000-0000-4000-8000-000000000001","idempotency_key":"30000000-0000-4000-8000-000000000001"}
```

정보 수정: 비밀번호를 바꾸지 않으면 current_password/new_password를 생략합니다.

```json
{"name":"홍길동","phone":"010-9999-8888","address":"서울시 새주소 123","current_password":"my-password123","new_password":"changed-password123"}
```

탈퇴 (DELETE 본문):

```json
{"password":"changed-password123"}
```

## 응답 구조

회원정보는 id/email/name/phone/address/created_at/role만 반환하며 해시·token_version은 공개하지 않습니다. 목록은 `items`, `page`, `has_more`를 반환합니다. 주문 객체는 orders 컬럼과 `items` 배열, `payment`를 포함합니다. SQL RPC의 payment는 객체 또는 null이고 PostgREST 조회의 payment는 배열일 수 있습니다. item의 `product`는 현재 상품 상태이고 product_name/unit_price는 주문 스냅샷입니다.

실패는 `{"detail":"한국어 안내"}`입니다. 입력 검증 실패는 `errors:[{"field":"필드명","message":"안내"}]`도 제공합니다. 401 로그인 필요, 403 CSRF 실패, 404 존재하지 않음/다른 회원 소유, 409 재고 부족·상태 충돌·중복 이메일, 422 형식 오류, 429 로그인 시도 제한, 503 DB 연결/설정 장애입니다. 입력값·비밀번호·원본 DB 오류를 반환하지 않습니다.

`/api/docs`도 제공하지만 외부 CDN을 차단하는 CSP 정책 때문에 Swagger UI가 브라우저에서 제한될 수 있습니다. 전체 API 계약은 외부 스크립트 없이 읽을 수 있는 이 문서와 `/openapi.json`을 기준으로 합니다.
