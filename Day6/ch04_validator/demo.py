from datetime import date
from pydantic import BaseModel, Field, ValidationError, field_validator,model_validator

class Signup(BaseModel):
    username: str= Field(min_length=3)
    password:str =Field(min_length=8)
    password_confirm:str
    tags: list[str]=[]

    @field_validator("username")
    @classmethod
    def normal_username(cls,value:str)-> str:
        text= value.strip().lower()
        if ' ' in text:
            raise ValueError('아이디에는 공백을 사용할 수 없습니다')
        return text

    @field_validator('tags',mode='before')
    @classmethod
    def parse_tags(cls, value:object)->object:
        if isinstance(value,str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value

    @model_validator(mode='after')
    def verify_password(self) ->'Signup':
        if self.password != self.password_confirm:
            raise ValueError('비밀번호가 일치하지 않습니다.')
        return self

class Reservation(BaseModel):
    start:date
    end:date

    @model_validator(mode='after')
    def validate_period(self)->'Reservation':
        if self.start > self.end:
            raise ValueError('종료일은 시작일보다 클수 없습니다.')
        return self

def main() -> None:
    signup = Signup(username='  STUDENT01  ', password='password12',
                    password_confirm='password12', tags='python, api')
    print('STEP 1 - 전처리와 교차 검증:', signup.username, signup.tags)
    print('STEP 2 - 날짜 유효성:', Reservation(start='2026-10-21', end='2026-10-22'))
    try:
        Signup(username='goodname', password='password12', password_confirm='wrong')
    except ValidationError as error:
        print('STEP 3 - 검증 실패:', error.errors()[0]['type'])


if __name__ == '__main__':
    main()