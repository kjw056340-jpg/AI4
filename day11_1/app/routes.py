from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from app.schemas import CartItem, Checkout, DeleteAccount, Login, Payment, Profile, Quantity, Register
from app.security import (clear_auth, csrf_token, current_user, get_db, hash_password,
                          public_user, safe_next, set_auth, verify_password)

router = APIRouter(prefix='/api')
# 없는 계정도 같은 비용으로 bcrypt를 검사해 계정 존재 여부의 시간차를 줄입니다.
DUMMY_HASH = hash_password('dummy-password-12345')
ORDER_SELECT = '*,items:order_items(*,product:products(id,name,price,stock,image_key,is_active)),payment:payments(*)'


@router.get('/csrf', tags=['인증'])
def csrf(request: Request, response: Response):
    return {'csrf_token': csrf_token(request, response)}


@router.post('/auth/register', status_code=201, tags=['인증'])
def register(body: Register, response: Response, db=Depends(get_db)):
    data = body.model_dump(exclude={'password'})
    data['email'] = str(body.email).lower()
    data['password_hash'] = hash_password(body.password)
    user = db.request('POST', 'users', data=data)[0]
    set_auth(response, user)
    return {'user': public_user(user)}


@router.post('/auth/login', tags=['인증'])
def login(body: Login, response: Response, next: str = '/products', db=Depends(get_db)):
    users = db.select('users', select='*', email=f'eq.{str(body.email).lower()}', is_active='eq.true', limit='1')
    user = users[0] if users else None
    valid = verify_password(body.password, user['password_hash'] if user else DUMMY_HASH)
    if not user or not valid:
        raise HTTPException(401, '이메일 또는 비밀번호를 확인해 주세요.')
    set_auth(response, user)
    return {'user': public_user(user), 'next': safe_next(next)}


@router.post('/auth/logout', tags=['인증'])
def logout(response: Response, user=Depends(current_user), db=Depends(get_db)):
    db.mutate(user, 'logout')
    clear_auth(response)
    return {'message': '로그아웃했습니다.'}


@router.get('/me', tags=['회원'])
def me(user=Depends(current_user)):
    return public_user(user)


@router.patch('/me', tags=['회원'])
def profile(body: Profile, response: Response, user=Depends(current_user), db=Depends(get_db)):
    data = body.model_dump(exclude={'current_password', 'new_password'})
    if body.new_password is not None:
        if not verify_password(body.current_password, user['password_hash']):
            raise HTTPException(400, '현재 비밀번호가 일치하지 않습니다.')
        data['password_hash'] = hash_password(body.new_password)
    updated = db.mutate(user, 'profile', data)
    if body.new_password is not None:
        set_auth(response, updated)
    return public_user(updated)


@router.delete('/me', tags=['회원'])
def delete_account(body: DeleteAccount, response: Response, user=Depends(current_user), db=Depends(get_db)):
    if not verify_password(body.password, user['password_hash']):
        raise HTTPException(400, '비밀번호가 일치하지 않습니다.')
    db.mutate(user, 'delete_account')
    clear_auth(response)
    return {'message': '탈퇴가 완료되었습니다. 개인정보는 익명화되었습니다.'}


@router.get('/products', tags=['상품'])
def products(category: str | None = Query(None, max_length=30),
             page: int = Query(1, ge=1, le=10000), db=Depends(get_db)):
    params = {'select': 'id,name,description,category,price,stock,image_key',
              'is_active': 'eq.true', 'order': 'created_at.desc,id.asc',
              'limit': '13', 'offset': str((page - 1) * 12)}
    if category:
        params['category'] = f'eq.{category}'
    rows = db.select('products', **params)
    return {'items': rows[:12], 'page': page, 'has_more': len(rows) > 12}


@router.get('/products/{product_id}', tags=['상품'])
def product(product_id: UUID, db=Depends(get_db)):
    rows = db.select('products', select='id,name,description,category,price,stock,image_key',
                     id=f'eq.{product_id}', is_active='eq.true', limit='1')
    if not rows:
        raise HTTPException(404, '상품을 찾을 수 없습니다.')
    return rows[0]


@router.get('/cart', tags=['장바구니'])
def cart(user=Depends(current_user), db=Depends(get_db)):
    rows = db.select('orders', select=ORDER_SELECT, user_id=f"eq.{user['id']}", status='eq.CART', limit='1')
    return rows[0] if rows else {'id': None, 'status': 'CART', 'items': [], 'total_amount': 0}


@router.post('/cart/items', tags=['장바구니'])
def cart_add(body: CartItem, user=Depends(current_user), db=Depends(get_db)):
    return db.mutate(user, 'cart_add', body.model_dump(mode='json'))


@router.patch('/cart/items/{product_id}', tags=['장바구니'])
def cart_set(product_id: UUID, body: Quantity, user=Depends(current_user), db=Depends(get_db)):
    return db.mutate(user, 'cart_set', {'product_id': str(product_id), 'quantity': body.quantity})


@router.delete('/cart/items/{product_id}', tags=['장바구니'])
def cart_remove(product_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    return db.mutate(user, 'cart_remove', {'product_id': str(product_id)})


@router.post('/orders/checkout', status_code=201, tags=['주문'])
def checkout(body: Checkout, user=Depends(current_user), db=Depends(get_db)):
    return db.mutate(user, 'checkout', body.model_dump(mode='json'))


@router.get('/orders', tags=['주문'])
def orders(page: int = Query(1, ge=1, le=10000), user=Depends(current_user), db=Depends(get_db)):
    rows = db.select('orders', select=ORDER_SELECT, user_id=f"eq.{user['id']}",
                     status='neq.CART', order='created_at.desc', limit='11', offset=str((page - 1) * 10))
    return {'items': rows[:10], 'page': page, 'has_more': len(rows) > 10}


@router.get('/orders/{order_id}', tags=['주문'])
def order(order_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    rows = db.select('orders', select=ORDER_SELECT, id=f'eq.{order_id}', user_id=f"eq.{user['id']}", status='neq.CART', limit='1')
    if not rows:
        raise HTTPException(404, '주문을 찾을 수 없습니다.')
    return rows[0]


@router.post('/orders/{order_id}/cancel', tags=['주문'])
def cancel(order_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    return db.mutate(user, 'cancel', {'order_id': str(order_id)})


@router.post('/payments', tags=['결제'])
def payment(body: Payment, user=Depends(current_user), db=Depends(get_db)):
    # 금액·user_id·결제상태는 클라이언트 입력을 받지 않습니다.
    return db.mutate(user, 'pay', body.model_dump(mode='json'))


@router.get('/payments/{payment_id}', tags=['결제'])
def payment_detail(payment_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    rows = db.select('payments', select='*', id=f'eq.{payment_id}', user_id=f"eq.{user['id']}", limit='1')
    if not rows:
        raise HTTPException(404, '결제 기록을 찾을 수 없습니다.')
    return rows[0]
