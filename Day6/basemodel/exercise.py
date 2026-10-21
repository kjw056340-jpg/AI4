from pydantic import BaseModel, Field


class Product(BaseModel):
    # TODO title: 최소 2자, 최대 60자
    title : str = Field(min_length=2, max_length=60)
    # TODO price: 0보다 커야 함
    price : int =Field(ge=0)
    # TODO stock: 0 이상, 기본값 0
    stock :int=Field(ge=0, default=0)
    # TODO sku: SKU-와 숫자 네 자리 패턴
    sku : str = Field(pattern=r'^SKU-[0-9]{4}$') 
    


invalid_cases = [
        {'title': 'A'},
        {'title': 'A' * 61},
        {'price': 0},
        {'stock': -1},
        {'sku': 'SKU-001'},
    ]
for changes in invalid_cases:
        data = product.model_dump()
        data.update(changes)
        try:
            Product(**data)
        except ValidationError as error:
            print('검증 실패:', changes)
            for detail in error.errors():
                print(detail['loc'], detail['type'])
        else:
            raise AssertionError(f'잘못된 입력이 검증을 통과했습니다: {changes}')

if __name__ == '__main__':
    main()