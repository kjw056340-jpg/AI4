from pydantic import BaseModel, ValidationError

# TODO : Book 모델의 필드를 정의하세요

# title:str(필수),price:int(필수),in_stock:bool=True,note:str|None=None
class Book(BaseModel):
    title: str
    price: int
    in_stock: bool = True
    note: str | None = None


def main() -> None:
    # TODO: Book(title='파이썬 기초', price='19000') 만들기
    book = Book(title='파이썬 기초', price='19000')

    # TODO: model_dump() 호출, 가격이 int로 변환되었는지 확인
    data = book.model_dump()
    print(data)

    # TODO: title 누락 시 ValidationError 확인
    try:
        book2= Book(price=20000)
    except ValidationError as e:
        print('error', e.errors()[0])


if __name__ == '__main__':
    main()