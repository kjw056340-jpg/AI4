#필수/기본값, 모델 생성/검증
from pydantic import BaseModel,ValidationError

class Member(BaseModel):
    username : str
    age : int
    active :bool = True
    nickname : str | None=None

class MemberOut(Member):
    id : int

def main() -> None:
    member=Member(username='lee',age=20)
    print(member)
    raw={'username':'kim','age':'34','active':False}
    parsed=Member.model_validate(raw)
    print(parsed,'age타입',type(parsed.age).__name__)
    print('nickname 기본값',parsed.nickname)

    #필수 필드 누락
    try:
        Member(username='kim',age=20)
        #Member.model_validate({'username':'kim'})

    #memberout 객체생성
        memberout= MemberOut(id=1,username='lee',age=20)
        print(memberout)

    except ValidationError as e:
        print(e.errors()[0]['loc'],e.errors()[0]['type'])

    #memberout 객체생성
    memberout= MemberOut(id=1)
    print(memberout)


if __name__ == '__main__':
    main()


# 필수/기본값, 모델 생성/검증
from pydantic import BaseModel,ValidationError

class Member(BaseModel):
    username : str
    age : int
    active : bool = True
    nickname : str | None = None

class MemberOut(Member):
    id : int

def main() ->None:
    member = Member(username = 'lee',age = 20)
    print(member)
    raw = {'username':'kim', 'age':'34','active':False}
    parsed = Member.model_validate(raw)
    print(parsed, 'age 타입',type(parsed.age).__name__)
    print('nickname 기본값', parsed.nickname)

    # 필수 필드 누락
    try:
        Member(username='kim',age=20)
        # Member.model_validate({'username':'kim'})
        
        # memberout 객체생성
        memberout = MemberOut(id=1,username='lee',age=20)
        print(memberout)
    except ValidationError as e:
        print(e.errors()[0]['loc'], e.errors()[0]['type'])
    
    
if __name__ == '__main__':
    main()