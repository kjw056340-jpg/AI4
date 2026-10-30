# 테이블 정의서

이 문서는 [CREATE TABLE SQL](sql/001_schema.sql)에 [Supabase Auth 변경](sql/004_supabase_auth.sql)을 적용한 컬럼 정의입니다. 먼저 [최소 ERD](erd.md)로 관계를 보고, 필요한 컬럼만 이 문서에서 확인하면 됩니다.

모든 금액은 **원(KRW) 단위의 정수**입니다. PK는 자동 생성 UUID입니다. 아래에서 `필수`는 SQL의 `NOT NULL`을 뜻하며, 기본값이 있으면 INSERT 시 생략할 수 있습니다. `text`의 글자 수 제한은 별도의 CHECK가 있는 경우만 DB가 직접 보장합니다.

## 1. users — 회원

프로필·권한·기본 배송정보를 저장합니다. 인증과 비밀번호는 Supabase의 `auth.users`가 담당하며 `auth_user_id`로 연결합니다.

| 컬럼 | 자료형 | 필수 | 설명·제약 |
| --- | --- | --- | --- |
| `id` | uuid | O | PK, 자동 생성 |
| `email` | text | O | 로그인 이메일, UNIQUE, 소문자, 254자 이하 |
| `auth_user_id` | uuid | - | UNIQUE, auth.users(id) FK. 기존 회원은 확인 후 연결 |
| `role` | text | O | member/admin, 기본 member. 서버에서만 변경 |
| `password_hash` | text | - | 이전 인증의 잔여 컬럼. 앱에서 사용하지 않으며 회원 연결 확인 후 NULL로 정리 |
| `name` | text | O | 이름, 1~60자 |
| `phone` | text | O | 기본 연락처, 기본값 `''`, 30자 이하 |
| `address` | text | O | 기본 주소, 기본값 `''`, 300자 이하 |
| `token_version` | integer | O | 로그인 무효화용 번호, 기본값 0, 0 이상 |
| `is_active` | boolean | O | 계정 활성 여부, 기본값 true |
| `created_at` | timestamptz | O | 가입 시각, 기본값 현재 시각 |
| `updated_at` | timestamptz | O | 정보 수정 시각, 기본값 현재 시각 |

회원정보 수정은 이 테이블을 UPDATE합니다. 로그아웃·비밀번호 변경 시 `token_version`을 올려 이전 JWT를 무효화합니다. 탈퇴 시 행을 삭제하는 대신 개인정보를 익명화하고 `is_active=false`로 바꿉니다.

## 2. products — 상품

상품 목록·상세 화면에서 읽고, 결제 성공 시 재고를 차감합니다.

| 컬럼 | 자료형 | 필수 | 설명·제약 |
| --- | --- | --- | --- |
| `id` | uuid | O | PK, 자동 생성 |
| `name` | text | O | 상품명, 1~120자 |
| `description` | text | O | 상품 설명 |
| `category` | text | O | 카테고리 |
| `price` | bigint | O | 현재 판매가, 1~100,000,000원 |
| `stock` | integer | O | 재고, 기본값 0, 0 이상 |
| `image_key` | text | O | 로컬 이미지 키, 기본값 `mug`; `mug/lamp/chair/bag/clock/vase`만 허용 |
| `is_active` | boolean | O | 판매 여부, 기본값 true |
| `created_at` | timestamptz | O | 등록 시각, 기본값 현재 시각 |

상품은 판매 중지 시 `is_active=false`로 바꿉니다. 주문에 사용된 상품을 삭제하면 구매내역 연결이 끊기므로 FK로 삭제를 제한합니다.

## 3. orders — 장바구니·주문

누가 주문했는지, 주문 상태와 총액, 주문 당시 배송정보를 저장합니다.

| 컬럼 | 자료형 | 필수 | 설명·제약 |
| --- | --- | --- | --- |
| `id` | uuid | O | PK, 자동 생성 |
| `user_id` | uuid | O | FK → `users.id`, 회원 삭제 제한 |
| `status` | text | O | 기본값 `CART`; `CART/ORDERED/PAID/CANCELED`만 허용 |
| `total_amount` | bigint | O | 상품별 단가 × 수량의 합계, 기본값 0, 0 이상 |
| `recipient` | text | O | 주문 당시 받는 분, 기본값 `''` |
| `phone` | text | O | 주문 당시 연락처, 기본값 `''` |
| `address` | text | O | 주문 당시 배송지, 기본값 `''` |
| `created_at` | timestamptz | O | 행 생성 시각, 기본값 현재 시각 |
| `ordered_at` | timestamptz | — | 주문 확정 시각, 장바구니일 때 NULL |
| `paid_at` | timestamptz | — | 결제 완료 시각, 미결제일 때 NULL |

주요 규칙:

- 회원별 `status='CART'`인 행은 부분 UNIQUE 인덱스로 최대 하나만 허용합니다.
- `ORDERED`, `PAID`는 `total_amount > 0`, `ordered_at IS NOT NULL`이어야 합니다.
- `PAID`는 `paid_at IS NOT NULL`이어야 합니다.
- 주문 생성 API와 DB 함수가 받는 분·연락처·배송지 입력을 검사합니다.
- 주문의 배송정보를 별도 저장하므로 이후 회원의 기본 주소가 바뀌어도 기존 주문 주소는 유지됩니다. 탈퇴 시에는 주문 배송정보도 익명화합니다.

## 4. order_items — 장바구니·주문 상품

주문 안에 어떤 상품을 몇 개 담았는지 저장합니다. **주문 한 건과 주문상품 한 건은 다른 개념**입니다.

| 컬럼 | 자료형 | 필수 | 설명·제약 |
| --- | --- | --- | --- |
| `id` | uuid | O | PK, 자동 생성 |
| `order_id` | uuid | O | FK → `orders.id`, 주문 삭제 시 항목도 삭제 |
| `product_id` | uuid | O | FK → `products.id`, 상품 삭제 제한 |
| `product_name` | text | O | 주문에 저장한 상품명 |
| `unit_price` | bigint | O | 주문에 저장한 개당 가격, 1~100,000,000원 |
| `quantity` | integer | O | 구매 수량, 1~99개 |

`(order_id, product_id)`는 UNIQUE입니다. 같은 장바구니에 같은 상품을 다시 담으면 새 행을 만들지 않고 기존 행의 수량을 늘립니다.

장바구니에서는 담기·수량 변경 시 해당 상품의 현재 가격을 반영하고, 주문 확정 시 **모든 항목의 상품명과 가격을 다시 저장**합니다. 확정 후에는 상품 마스터가 바뀌어도 구매 당시 내역을 유지합니다.

## 5. payments — 결제

성공한 모의 결제만 저장합니다. 결제 대기나 재고 부족으로 실패한 요청에는 행을 만들지 않습니다.

| 컬럼 | 자료형 | 필수 | 설명·제약 |
| --- | --- | --- | --- |
| `id` | uuid | O | PK, 자동 생성 |
| `order_id` | uuid | O | FK → `orders.id`, UNIQUE, 주문 삭제 제한 |
| `user_id` | uuid | O | FK → `users.id`, 회원 삭제 제한 |
| `amount` | bigint | O | 실제 처리한 모의 결제 금액, 0보다 큼 |
| `status` | text | O | 기본값 `SUCCEEDED`, 이 값만 허용 |
| `method` | text | O | 기본값 `MOCK`, 이 값만 허용 |
| `idempotency_key` | uuid | O | 결제 재시도 구분 번호 |
| `created_at` | timestamptz | O | 결제 시각, 기본값 현재 시각 |

`order_id UNIQUE`로 주문별 성공 결제를 한 건만 허용합니다. `(user_id, idempotency_key)`도 UNIQUE입니다. 이미 결제된 주문을 다시 요청하면 기존 결과를 반환하고 재고를 다시 차감하지 않습니다.

**서버 전용 결제 함수가 보장하는 규칙:** 결제 회원과 주문 회원의 일치, `payments.amount = orders.total_amount`, 재고 확인·차감·결제 기록·주문 상태 변경의 동시 성공입니다. 이 규칙들은 각각 단독 CHECK 제약으로 구현된 것은 아닙니다.

## 조회용 인덱스

| 대상 | 인덱스 | 목적 |
| --- | --- | --- |
| users | email UNIQUE | 이메일 중복 방지·로그인 조회 |
| orders | user_id, CART 조건 UNIQUE | 회원별 장바구니 중복 방지 |
| orders | user_id, created_at 내림차순 | 내 주문내역 조회 |
| order_items | order_id, product_id UNIQUE | 같은 주문의 상품 중복 방지·항목 조회 |
| order_items | product_id | 상품별 주문 연결 조회 |
| payments | order_id UNIQUE | 주문별 중복 결제 방지 |
| payments | user_id, idempotency_key UNIQUE | 결제 요청 번호 중복 방지 |
| payments | user_id, created_at 내림차순 | 내 결제내역 조회 |
| products | category, created_at 내림차순, 판매 중 조건 | 판매 상품 목록 조회 |

모든 테이블은 RLS를 활성화하고 브라우저용 역할의 직접 접근을 막습니다. 서버만 Supabase 서버 키를 사용하며, 요청한 회원의 소유권을 확인합니다.
