from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class Schema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @field_validator('name', 'phone', 'address', 'recipient', check_fields=False)
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip()


def password_valid(value: str) -> str:
    # bcrypt는 바이트 단위 72바이트 제한이 있으므로 한글 비밀번호도 검증합니다.
    if len(value) < 10 or len(value.encode('utf-8')) > 72:
        raise ValueError('비밀번호는 10자 이상, UTF-8 기준 72바이트 이하여야 합니다.')
    if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
        raise ValueError('비밀번호에는 문자와 숫자를 모두 포함해 주세요.')
    return value


class Login(Schema):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=1, max_length=72, strict=True)

    @field_validator('password')
    @classmethod
    def byte_limit(cls, value: str) -> str:
        if len(value.encode('utf-8')) > 72:
            raise ValueError('비밀번호가 너무 깁니다.')
        return value


class Register(Login):
    name: str = Field(min_length=1, max_length=60)
    phone: str = Field(default='', max_length=30, pattern=r'^[0-9+()\s-]*$')
    address: str = Field(default='', max_length=300)
    _password_policy = field_validator('password')(password_valid)


class Profile(Schema):
    name: str = Field(min_length=1, max_length=60)
    phone: str = Field(default='', max_length=30, pattern=r'^[0-9+()\s-]*$')
    address: str = Field(default='', max_length=300)
    current_password: str | None = Field(default=None, max_length=72)
    new_password: str | None = Field(default=None, max_length=72)

    @model_validator(mode='after')
    def check_password(self):
        if self.new_password is not None:
            password_valid(self.new_password)
            if not self.current_password:
                raise ValueError('비밀번호 변경 시 현재 비밀번호를 입력해 주세요.')
        return self


class DeleteAccount(Schema):
    password: str = Field(min_length=1, max_length=72)


class CartItem(Schema):
    product_id: UUID
    quantity: int = Field(ge=1, le=99, strict=True)


class Quantity(Schema):
    quantity: int = Field(ge=1, le=99, strict=True)


class Checkout(Schema):
    source: Literal['cart', 'direct']
    product_id: UUID | None = None
    quantity: int = Field(default=1, ge=1, le=99, strict=True)
    recipient: str = Field(min_length=1, max_length=60)
    phone: str = Field(min_length=7, max_length=30, pattern=r'^[0-9+()\s-]+$')
    address: str = Field(min_length=5, max_length=300)

    @model_validator(mode='after')
    def direct_product(self):
        if self.source == 'direct' and not self.product_id:
            raise ValueError('바로 구매할 상품을 선택해 주세요.')
        return self


class Payment(Schema):
    order_id: UUID
    idempotency_key: UUID
