from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from app.schemas import CartItem, Checkout, DeleteAccount, Login, Payment, Profile, Quantity, Register, ProductWrite
from app.security import (clear_auth, csrf_token, current_user, get_db, get_auth, admin_user,
                          public_user, safe_next, set_auth, auth_profile,
                          SUPABASE_COOKIE, refresh_session)

router = APIRouter(prefix='/api')
ORDER_SELECT = '*,items:order_items(*,product:products(id,name,price,stock,image_key,is_active)),payment:payments(*)'


@router.get('/csrf', tags=['인증'])
def csrf(request: Request, response: Response):
    return {'csrf_token': csrf_token(request, response)}


@router.post('/auth/register', status_code=201, tags=['인증'])
def register(body: Register, response: Response, db=Depends(get_db), auth=Depends(get_auth)):
    data = body.model_dump(exclude={'password'})
    data['email'] = str(body.email).lower()
    session = auth.signup({'email': data.pop('email'), 'password': body.password, 'data': data})
    if not session.get('access_token'):
        return {'user': None, 'confirmation_required': True,
                'message': '이메일의 인증 링크를 누른 후 로그인해 주세요.'}
    user = auth_profile(session['user'], db)
    set_auth(response, user, session)
    return {'user': public_user(user)}


@router.post('/auth/login', tags=['인증'])
def login(body: Login, response: Response, next: str = '/products', db=Depends(get_db), auth=Depends(get_auth)):
    session = auth.login(str(body.email).lower(), body.password)
    user = auth_profile(session['user'], db)
    set_auth(response, user, session)
    return {'user': public_user(user), 'next': safe_next(next)}


@router.post('/auth/logout', tags=['인증'])
def logout(request: Request, response: Response, user=Depends(current_user), db=Depends(get_db), auth=Depends(get_auth)):
    auth.logout(request.cookies[SUPABASE_COOKIE])
    db.mutate(user, 'logout')
    clear_auth(response)
    return {'message': '로그아웃했습니다.'}


@router.post('/auth/refresh', tags=['인증'])
def refresh(request: Request, response: Response, db=Depends(get_db), auth=Depends(get_auth)):
    user, session = refresh_session(request, db, auth)
    set_auth(response, user, session)
    return {'user': public_user(user)}


@router.get('/me', tags=['회원'])
def me(user=Depends(current_user)):
    return public_user(user)


@router.patch('/me', tags=['회원'])
def profile(body: Profile, request: Request, response: Response, user=Depends(current_user), db=Depends(get_db), auth=Depends(get_auth)):
    data = body.model_dump(exclude={'current_password', 'new_password'})
    if body.new_password is not None:
        verified = auth.login(user['email'], body.current_password)
        auth.password(verified['access_token'], body.new_password)
        auth.logout(verified['access_token'])
        db.mutate(user, 'logout')
        user = {**user, 'token_version': user['token_version'] + 1}
    updated = db.mutate(user, 'profile', data)
    if body.new_password is not None:
        session = auth.login(user['email'], body.new_password)
        set_auth(response, updated, session)
    return public_user(updated)


@router.delete('/me', tags=['회원'])
def delete_account(body: DeleteAccount, response: Response, user=Depends(current_user), db=Depends(get_db), auth=Depends(get_auth)):
    verified = auth.login(user['email'], body.password)
    auth.logout(verified['access_token'])
    db.mutate(user, 'delete_account')
    try:
        auth.delete_user(user['auth_user_id'])
    except HTTPException:
        raise HTTPException(503, '쇼핑몰 계정은 비활성화되었습니다. 인증 계정 정리를 관리자에게 요청해 주세요.') from None
    clear_auth(response)
    return {'message': '탈퇴가 완료되었습니다. 개인정보는 익명화되었습니다.'}


@router.post('/admin/products', status_code=201, tags=['관리자'])
def create_product(body: ProductWrite, user=Depends(admin_user), db=Depends(get_db)):
    return db.request('POST', 'products', data=body.model_dump())[0]


@router.put('/admin/products/{product_id}', tags=['관리자'])
def update_product(product_id: UUID, body: ProductWrite, user=Depends(admin_user), db=Depends(get_db)):
    rows = db.request('PATCH', 'products', params={'id': f'eq.{product_id}'}, data=body.model_dump())
    if not rows:
        raise HTTPException(404, '상품을 찾을 수 없습니다.')
    return rows[0]


@router.get('/admin/orders', tags=['관리자'])
def admin_orders(page: int = Query(1, ge=1, le=10000), user=Depends(admin_user), db=Depends(get_db)):
    rows = db.select('orders', select=ORDER_SELECT, status='neq.CART', order='created_at.desc',
                     limit='11', offset=str((page - 1) * 10))
    return {'items': rows[:10], 'page': page, 'has_more': len(rows) > 10}


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
