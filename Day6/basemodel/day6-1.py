# pydantic
# 데이터의 유효성 및 타입을 체크
# 기능이 구현된 클래스를 상속받아서 pydantic 클래스 또는 모델을 만들 수 있음
from pydantic import BaseModel,ValidationError
# 일반 파이썬 클래스
class NormalClass:
    def __init__(self, name: str, age: int):
        # 객체변수(인스턴스변수)
        self.name = name
        self.age = age

#params={'age':20,'name':'홍길동'}
user1= NormalClass(name='홍길동',age=20)
#user1=NormalClass(**params)

print('일반클래스',user1.age)
print('데이터 타입',type(user1.age))

#pydantic 클래스
class PydanticUser(BaseModel):
    name:str
    age:int

user2=PydanticUser(name='홍길동',age=20)
print('일반클래스',user2.age)
print('데이터 타입',type(user2.age))

user3=PydanticUser(name='홍길동',age=20)
print('일반클래스',user3.age)
print('데이터 타입',type(user3.age))
