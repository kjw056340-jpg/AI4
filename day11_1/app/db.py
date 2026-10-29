import logging
from typing import Any

import httpx
from fastapi import HTTPException

from app.config import Settings

logger = logging.getLogger(__name__)
ERRORS = {
    'AUTH_REQUIRED': (401, '로그인이 만료되었습니다. 다시 로그인해 주세요.'),
    'NOT_FOUND': (404, '요청한 항목을 찾을 수 없습니다.'),
    'OUT_OF_STOCK': (409, '재고가 부족합니다. 수량을 확인해 주세요.'),
    'PRODUCT_UNAVAILABLE': (409, '현재 구매할 수 없는 상품이 포함되어 있습니다.'),
    'QUANTITY_INVALID': (422, '상품 수량은 1개에서 99개까지 선택할 수 있습니다.'),
    'CART_LIMIT': (409, '장바구니에는 최대 50종의 상품을 담을 수 있습니다.'),
    'EMPTY_CART': (409, '장바구니에 상품을 먼저 담아 주세요.'),
    'INVALID_STATUS': (409, '현재 주문 상태에서는 처리할 수 없습니다.'),
    'KEY_REUSED': (409, '다른 결제에 사용된 요청 번호입니다.'),
    'SHIPPING_REQUIRED': (422, '받는 분, 연락처와 배송지를 확인해 주세요.'),
    'INVALID_REQUEST': (422, '요청 내용을 확인해 주세요.'),
}


class Database:
    def __init__(self, settings: Settings):
        headers = {'apikey': settings.supabase_key, 'Content-Type': 'application/json'}
        # 신규 secret 키는 apikey만, legacy JWT service_role 키는 Bearer도 사용합니다.
        if not settings.supabase_key.startswith('sb_secret_'):
            headers['Authorization'] = f'Bearer {settings.supabase_key}'
        self.client = httpx.Client(base_url=f'{settings.supabase_url}/rest/v1/',
                                   headers=headers, timeout=15)

    def close(self):
        self.client.close()

    def request(self, method: str, path: str, *, params=None, data=None) -> Any:
        try:
            response = self.client.request(method, path, params=params, json=data,
                                           headers={'Prefer': 'return=representation'})
        except httpx.RequestError:
            raise HTTPException(503, '데이터베이스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.') from None
        if response.is_error:
            try:
                error = response.json()
            except ValueError:
                error = {}
            message = error.get('message', '')
            if message in ERRORS:
                status, detail = ERRORS[message]
                raise HTTPException(status, detail)
            if error.get('code') == '23505':
                raise HTTPException(409, '이미 등록된 정보입니다. 이메일 또는 결제 내역을 확인해 주세요.')
            # 비밀키/개인정보가 섞일 수 있는 응답 본문은 로그에 기록하지 않습니다.
            logger.error('Database request failed: status=%s code=%s', response.status_code, error.get('code'))
            raise HTTPException(503, '데이터를 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.')
        return response.json() if response.content else None

    def select(self, table: str, **params):
        return self.request('GET', table, params=params)

    def mutate(self, user: dict, action: str, data: dict | None = None):
        return self.request('POST', 'rpc/shop_mutate', data={
            'p_user': user['id'], 'p_version': user['token_version'],
            'p_action': action, 'p_data': data or {},
        })
