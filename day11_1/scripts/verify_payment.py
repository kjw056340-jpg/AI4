r"""현재 .env의 Supabase를 사용하는 실제 모의 결제 검증.

실행: .\.venv\Scripts\python.exe scripts/verify_payment.py
고유한 테스트 회원/상품만 만들고 finally에서 해당 데이터만 삭제합니다.
실제 PG 호출 또는 기존 상품의 재고 변경은 없습니다.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import secrets
import argparse
import httpx
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.config import get_settings
from app.db import Database
from app.main import app

SHIPPING = {'recipient': '결제 검증용 수령인', 'phone': '010-0000-0000',
            'address': '테스트 전용 가상 배송지 123'}


def main(base_url=None):
    settings = get_settings()
    admin = Database(settings)
    run = uuid4().hex
    product_id = str(uuid4())
    emails = [f'payment-qa-{run}-{n}@example.com' for n in (1, 2)]
    password = secrets.token_urlsafe(24) + 'Aa123'
    results = []
    cleanup_ok = False
    failure = None
    order_ids = []
    payment_ids = []
    if base_url and base_url.rstrip('/') != settings.app_origin:
        raise SystemExit('검증 주소와 APP_ORIGIN이 일치해야 합니다.')

    def make_client():
        if base_url:
            return httpx.Client(base_url=base_url, timeout=30)
        return TestClient(app, base_url=settings.app_origin)

    def record(name, detail):
        results.append((name, detail))
        print('PASS: ' + name + ' — ' + detail, flush=True)

    def expect(response, status=200):
        if response.status_code != status:
            try:
                detail = response.json().get('detail', '요청 실패')
            except ValueError:
                detail = 'JSON 응답 없음'
            raise AssertionError(f'예상 HTTP {status}, 실제 {response.status_code}: {detail}')
        return response.json()

    def stock():
        rows = admin.select('products', select='stock', id=f'eq.{product_id}')
        return rows[0]['stock']

    def change_product(**data):
        admin.request('PATCH', 'products', params={'id': f'eq.{product_id}'}, data=data)

    def checkout(client, headers, source='direct', quantity=1):
        data = {'source': source, **SHIPPING}
        if source == 'direct':
            data.update(product_id=product_id, quantity=quantity)
        order = expect(client.post('/api/orders/checkout', headers=headers, json=data), 201)
        order_ids.append(order['id'])
        return order

    def pay(client, headers, order, key=None):
        return client.post('/api/payments', headers=headers, json={
            'order_id': order['id'], 'idempotency_key': key or str(uuid4())})

    try:
        admin.request('POST', 'products', data={
            'id': product_id, 'name': '결제 검증 전용 ' + run[:8], 'description': '자동 검증 후 삭제',
            'category': 'TEST_ONLY', 'price': 1000, 'stock': 10, 'image_key': 'mug'})
        with make_client() as buyer:
            # 두 번째 회원은 같은 앱/실DB를 사용하되 쿠키를 분리합니다.
            other = make_client()
            try:
                clients = [buyer, other]
                headers = []
                for client in clients:
                    csrf = expect(client.get('/api/csrf'))['csrf_token']
                    headers.append({'X-CSRF-Token': csrf, 'Origin': settings.app_origin})

                response = buyer.post('/api/payments', headers=headers[0], json={
                    'order_id': str(uuid4()), 'idempotency_key': str(uuid4())})
                expect(response, 401)
                record('비로그인 결제 차단', 'HTTP 401')

                users = []
                for n, client in enumerate(clients):
                    result = expect(client.post('/api/auth/register', headers=headers[n], json={
                        'email': emails[n], 'password': password, 'name': '결제 검증 회원',
                        'phone': SHIPPING['phone'], 'address': SHIPPING['address']}), 201)
                    users.append(result['user'])
                record('실DB 회원가입·인증', '테스트 회원 2명 생성, HttpOnly 쿠키 인증')

                h = headers[0]
                cart = expect(buyer.post('/api/cart/items', headers=h,
                                         json={'product_id': product_id, 'quantity': 2}))
                assert cart['status'] == 'CART' and cart['total_amount'] == 2000
                assert stock() == 10
                saved_cart = expect(buyer.get('/api/cart'))
                assert saved_cart['id'] == cart['id']
                assert saved_cart['items'][0]['product_id'] == product_id
                assert saved_cart['items'][0]['quantity'] == 2
                saved_rows = admin.select('order_items', select='id,quantity', order_id=f"eq.{cart['id']}")
                assert len(saved_rows) == 1 and saved_rows[0]['quantity'] == 2
                record('장바구니 저장·재조회', 'API와 실제 DB 모두 동일 상품 2개 저장 확인')
                order = checkout(buyer, h, source='cart')
                assert order['id'] == cart['id'] and order['status'] == 'ORDERED'
                assert stock() == 10
                record('장바구니 주문 확정', 'CART → ORDERED, 1,000원 × 2개, 결제 전 재고 10개 유지')

                key = str(uuid4())
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(pay, buyer, h, order, key) for _ in range(2)]
                    paid = [expect(f.result(timeout=40)) for f in futures]
                assert all(p['status'] == 'PAID' and p['payment']['amount'] == 2000 for p in paid)
                assert paid[0]['payment']['id'] == paid[1]['payment']['id']
                rows = admin.select('payments', select='id,amount', order_id=f"eq.{order['id']}")
                assert len(rows) == 1 and rows[0]['amount'] == 2000 and stock() == 8
                payment_ids.append(rows[0]['id'])
                record('결제·동시 중복 요청', '동시 요청 2회에도 결제 1건, 결제액 2,000원, 재고 10 → 8')

                retry = expect(pay(buyer, h, order, str(uuid4())))
                assert retry['payment']['id'] == rows[0]['id'] and stock() == 8
                record('결제 완료 후 재시도', '새 요청 번호로 재시도해도 추가 결제·추가 차감 없음')

                history = expect(buyer.get('/api/orders'))['items']
                found = next(o for o in history if o['id'] == order['id'])
                assert found['status'] == 'PAID' and found['payment']['id'] == rows[0]['id']
                detail = expect(buyer.get('/api/payments/' + rows[0]['id']))
                assert detail['amount'] == 2000
                record('구매내역·결제 상세', '결제 완료 주문 및 실제 payments 기록 조회 성공')

                cart2 = expect(buyer.post('/api/cart/items', headers=h,
                                          json={'product_id': product_id, 'quantity': 1}))
                direct = checkout(buyer, h)
                assert direct['id'] != cart2['id'] and direct['total_amount'] == 1000
                change_product(price=1500)
                direct_paid = expect(pay(buyer, h, direct))
                payment_ids.append(direct_paid['payment']['id'])
                assert direct_paid['payment']['amount'] == 1000 and stock() == 7
                assert direct_paid['items'][0]['unit_price'] == 1000
                preserved = expect(buyer.get('/api/cart'))
                assert preserved['id'] == cart2['id'] and preserved['items'][0]['quantity'] == 1
                record('바로 구매·가격 스냅샷', '기존 장바구니 보존, 가격 변경 후에도 확정 금액 1,000원으로 결제, 재고 8 → 7')

                expect(other.get('/api/orders/' + order['id']), 404)
                expect(other.get('/api/payments/' + rows[0]['id']), 404)
                expect(pay(other, headers[1], order), 404)
                assert stock() == 7
                record('다른 회원 주문·결제 차단', '조회 및 결제 요청 모두 HTTP 404, 재고 불변')

                pending = checkout(buyer, h)
                expect(buyer.post('/api/payments', headers=h, json={
                    'order_id': pending['id'], 'idempotency_key': str(uuid4()), 'amount': 1}), 422)
                expect(pay(buyer, h, pending, key), 409)
                assert stock() == 7
                record('금액 위조·요청 번호 재사용 차단', '클라이언트 amount 입력 HTTP 422, 타 주문의 결제 번호 재사용 HTTP 409')

                canceled = expect(buyer.post('/api/orders/' + pending['id'] + '/cancel', headers=h))
                assert canceled['status'] == 'CANCELED'
                expect(pay(buyer, h, pending), 409)
                assert not admin.select('payments', select='id', order_id=f"eq.{pending['id']}")
                record('취소 주문 결제 차단', 'HTTP 409, 결제 기록과 재고 변화 없음')

                insufficient = checkout(buyer, h, quantity=2)
                change_product(stock=1)
                expect(pay(buyer, h, insufficient), 409)
                unchanged = expect(buyer.get('/api/orders/' + insufficient['id']))
                assert unchanged['status'] == 'ORDERED' and unchanged['payment'] is None and stock() == 1
                assert not admin.select('payments', select='id', order_id=f"eq.{insufficient['id']}")
                record('재고 부족 결제 차단', 'HTTP 409, ORDERED 유지, payments 0건, 재고 1개 유지')

                last_orders = [checkout(buyer, h), checkout(other, headers[1])]
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(pay, clients[n], headers[n], last_orders[n]) for n in range(2)]
                    responses = [f.result(timeout=40) for f in futures]
                assert sorted(r.status_code for r in responses) == [200, 409]
                assert stock() == 0
                for response in responses:
                    if response.status_code == 200:
                        paid_last = expect(response)
                        assert paid_last['payment']['amount'] == 1500
                        payment_ids.append(paid_last['payment']['id'])
                last_ids = ','.join(o['id'] for o in last_orders)
                last_payments = admin.select('payments', select='id', order_id=f'in.({last_ids})')
                assert len(last_payments) == 1
                record('마지막 재고 동시 구매', '두 회원 동시 결제: 1건 성공·1건 재고 부족, 결제 1건, 재고 0개')
            finally:
                other.close()
    except Exception as error:
        failure = f'{type(error).__name__}: {error}'
        print('FAIL: ' + failure, flush=True)
    finally:
        try:
            # 이번 실행에서 만든 고유 이메일/UUID만 대상으로 정리합니다.
            users = admin.select('users', select='id', email='in.(' + ','.join(emails) + ')')
            uids = ','.join(u['id'] for u in users)
            if uids:
                orders = admin.select('orders', select='id', user_id=f'in.({uids})')
                oids = ','.join(o['id'] for o in orders)
                admin.request('DELETE', 'payments', params={'user_id': f'in.({uids})'})
                if oids:
                    admin.request('DELETE', 'order_items', params={'order_id': f'in.({oids})'})
                admin.request('DELETE', 'orders', params={'user_id': f'in.({uids})'})
                admin.request('DELETE', 'users', params={'id': f'in.({uids})'})
            admin.request('DELETE', 'products', params={'id': f'eq.{product_id}'})
            assert not admin.select('products', select='id', id=f'eq.{product_id}')
            assert not admin.select('users', select='id', email='in.(' + ','.join(emails) + ')')
            if order_ids:
                assert not admin.select('orders', select='id', id='in.(' + ','.join(order_ids) + ')')
            if payment_ids:
                assert not admin.select('payments', select='id', id='in.(' + ','.join(payment_ids) + ')')
            cleanup_ok = True
            print('CLEANUP: 테스트 회원·상품·주문·결제 정리 및 잔존 여부 확인 완료', flush=True)
        except Exception as error:
            print('CLEANUP_FAILED: ' + type(error).__name__, flush=True)
        admin.close()

    now = datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S KST')
    method = '실행 중인 실제 HTTP 서버' if base_url else 'FastAPI TestClient'
    report = ['# 실제 Supabase 모의 결제 검증 결과', '', f'- 실행 시각: {now}',
              f'- 방식: {method} → 실제 Supabase HTTP API → 실제 PostgreSQL 함수',
              '- 실제 PG 호출·금액 청구 없음. 고유한 테스트 회원·상품만 사용.',
              '- 기존 회원·상품·주문 데이터 및 기존 상품 재고는 변경하지 않음.', '',
              '| 검증 항목 | 결과 | 확인 내용 |', '| --- | --- | --- |']
    report += [f'| {name} | 통과 | {detail} |' for name, detail in results]
    report += ['', f'테스트 데이터 정리: {"완료" if cleanup_ok else "추가 확인 필요"}.', '']
    if failure:
        report += ['## 실패', '', failure, '']
    report += ['## 검증 범위', '',
               'API 인증·권한·실제 DB의 주문/결제 트랜잭션을 검증했습니다. 브라우저 화면의 클릭·결제 후 상품목록 이동, Render 배포 상태는 이번 검사에 포함하지 않았습니다.', '']
    (ROOT / 'docs' / '05_payment_verification.md').write_text('\n'.join(report), encoding='utf-8')
    print(f'RESULT: {len(results)}개 항목 통과, cleanup={cleanup_ok}, failed={failure is not None}', flush=True)
    return 1 if failure or not cleanup_ok else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='테스트 전용 데이터로 실제 DB의 장바구니/모의 결제를 검증합니다.')
    parser.add_argument('--base-url', help='실행 중인 실제 서버 주소. 생략하면 TestClient 사용')
    raise SystemExit(main(parser.parse_args().base_url))
