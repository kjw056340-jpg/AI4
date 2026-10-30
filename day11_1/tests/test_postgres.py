"""미리 schema.sql을 적용한 테스트 전용 Supabase/PostgreSQL에서 실행합니다.

각 테스트의 데이터는 rollback합니다. 동시성 테스트만 별도 UUID 행을 commit 후 정리합니다.
운영 DB를 연결하지 마세요. 앱은 이 연결 문자열을 사용하지 않습니다.
"""
import os
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import psycopg
import pytest
from psycopg.types.json import Jsonb

DSN = os.getenv('TEST_DATABASE_URL')
pytestmark = [pytest.mark.postgres, pytest.mark.skipif(not DSN, reason='TEST_DATABASE_URL이 없어 실제 DB 검증 생략')]
SHIPPING = {'recipient':'테스트 수령인','phone':'010-1234-5678','address':'서울시 테스트 주소 123'}


def mutate(conn, user, action, data=None, version=0):
    return conn.execute('select public.shop_mutate(%s,%s,%s,%s)',
                        (user,version,action,Jsonb(data or {}))).fetchone()[0]


def create_user(conn):
    uid=uuid4()
    conn.execute('insert into public.users(id,email,password_hash,name) values(%s,%s,%s,%s)',
                 (uid,f'{uid}@test.example','!test-only','테스트 사용자'))
    return uid


def create_product(conn, stock=10):
    pid=uuid4()
    conn.execute('insert into public.products(id,name,description,category,price,stock) values(%s,%s,%s,%s,1000,%s)',
                 (pid,'통합 테스트 상품','설명','테스트',stock))
    return pid


def direct(conn, uid, pid, qty=1):
    return mutate(conn,uid,'checkout',{'source':'direct','product_id':str(pid),'quantity':qty,**SHIPPING})


def pay(conn, uid, order, key=None):
    return mutate(conn,uid,'pay',{'order_id':str(order['id']),'idempotency_key':str(key or uuid4())})


@pytest.fixture
def conn():
    with psycopg.connect(DSN) as conn:
        try:
            yield conn
        finally:
            conn.rollback()


def test_cart_direct_purchase_and_snapshot(conn):
    uid=create_user(conn);pid=create_product(conn)
    cart=mutate(conn,uid,'cart_add',{'product_id':str(pid),'quantity':2})
    direct_order=direct(conn,uid,pid)
    assert direct_order['status']=='ORDERED' and direct_order['id']!=cart['id']
    assert conn.execute('select status from orders where id=%s',(cart['id'],)).fetchone()[0]=='CART'
    order=mutate(conn,uid,'checkout',{'source':'cart',**SHIPPING})
    conn.execute('update products set price=2000,name=%s where id=%s',('바뀐 이름',pid))
    paid=pay(conn,uid,order)
    assert paid['status']=='PAID' and paid['payment']['amount']==2000
    assert paid['items'][0]['product_name']=='통합 테스트 상품'
    assert conn.execute('select stock from products where id=%s',(pid,)).fetchone()[0]==8


def test_idempotent_payment_does_not_double_decrement(conn):
    uid=create_user(conn);pid=create_product(conn);order=direct(conn,uid,pid,2)
    key=uuid4();first=pay(conn,uid,order,key);again=pay(conn,uid,order,key)
    assert first['payment']['id']==again['payment']['id']
    assert conn.execute('select stock from products where id=%s',(pid,)).fetchone()[0]==8
    assert conn.execute('select count(*) from payments where order_id=%s',(order['id'],)).fetchone()[0]==1


def test_failed_payment_rolls_back_everything(conn):
    uid=create_user(conn);pid=create_product(conn);order=direct(conn,uid,pid,2)
    conn.execute('update products set stock=1 where id=%s',(pid,))
    with pytest.raises(psycopg.Error,match='OUT_OF_STOCK'):
        with conn.transaction(): pay(conn,uid,order)
    assert conn.execute('select stock from products where id=%s',(pid,)).fetchone()[0]==1
    assert conn.execute('select status from orders where id=%s',(order['id'],)).fetchone()[0]=='ORDERED'
    assert conn.execute('select count(*) from payments where order_id=%s',(order['id'],)).fetchone()[0]==0


def test_ownership_cancel_and_revocation(conn):
    uid=create_user(conn);other=create_user(conn);pid=create_product(conn);order=direct(conn,uid,pid)
    with pytest.raises(psycopg.Error,match='NOT_FOUND'):
        with conn.transaction(): pay(conn,other,order)
    canceled=mutate(conn,uid,'cancel',{'order_id':order['id']})
    assert canceled['status']=='CANCELED'
    with pytest.raises(psycopg.Error,match='INVALID_STATUS'):
        with conn.transaction(): pay(conn,uid,order)
    mutate(conn,uid,'logout')
    with pytest.raises(psycopg.Error,match='AUTH_REQUIRED'):
        with conn.transaction(): mutate(conn,uid,'cart_add',{'product_id':str(pid),'quantity':1})


def test_account_erasure_preserves_payment(conn):
    uid=create_user(conn);pid=create_product(conn);order=direct(conn,uid,pid);pay(conn,uid,order)
    pending=direct(conn,uid,pid)
    mutate(conn,uid,'delete_account')
    user=conn.execute('select is_active,phone,address,password_hash,email from users where id=%s',(uid,)).fetchone()
    assert user[0] is False and user[1:4]==('','',None)
    assert user[4].endswith('@deleted.invalid')
    assert conn.execute('select count(*) from payments where user_id=%s',(uid,)).fetchone()[0]==1
    assert conn.execute('select status,phone,address from orders where id=%s',(pending['id'],)).fetchone()==('CANCELED','','')


def test_roles_cannot_execute_or_read(conn):
    for role in ('anon','authenticated'):
        assert conn.execute("select has_function_privilege(%s,'public.shop_mutate(uuid,integer,text,jsonb)','EXECUTE')",(role,)).fetchone()[0] is False
        assert conn.execute("select has_table_privilege(%s,'public.users','SELECT')",(role,)).fetchone()[0] is False


def test_concurrent_last_stock_sale():
    # 서로 다른 사용자 둘이 마지막 재고를 동시에 결제해도 한 건만 성공해야 합니다.
    with psycopg.connect(DSN) as setup:
        a=create_user(setup);b=create_user(setup);pid=create_product(setup,1)
        oa=direct(setup,a,pid);ob=direct(setup,b,pid)
    def worker(uid,order):
        try:
            with psycopg.connect(DSN) as c:
                c.execute("set lock_timeout='5s'")
                pay(c,uid,order)
            return 'PAID'
        except psycopg.Error as error:
            return str(error)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(worker,a,oa),pool.submit(worker,b,ob)]
            results=[f.result(timeout=15) for f in futures]
        assert results.count('PAID')==1
        assert any('OUT_OF_STOCK' in result for result in results)
        with psycopg.connect(DSN) as c:
            assert c.execute('select stock from products where id=%s',(pid,)).fetchone()[0]==0
    finally:
        # 이 테스트에서 생성한 UUID 행만 제거합니다.
        with psycopg.connect(DSN) as c:
            c.execute('delete from payments where user_id=any(%s)',([a,b],))
            c.execute('delete from order_items where order_id in (select id from orders where user_id=any(%s))',([a,b],))
            c.execute('delete from orders where user_id=any(%s)',([a,b],))
            c.execute('delete from users where id=any(%s)',([a,b],))
            c.execute('delete from products where id=%s',(pid,))
