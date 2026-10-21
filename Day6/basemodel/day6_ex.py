from pydantic import BaseModel, ValidationError
from typing import Optional, Union 
class Student(BaseModel):
    name:str
    age:int  #'25' 숫자로 변경가능한 문자열숫자 입력하면 자동으로 숫자로 변환
    interests:list[str]
    #선택적으로 입력받는 nickname 필드추가(기본값은 None)
    nickname:Optional[str]=None #nickname=str |None 또는 Union[str,None]
    #학번 student_id 필드 추가(정수 또는 문자열 모두 허용)
    student_id: Union[int,str]


def main() -> None:
    #아래 데이터를 문자열 age= '123'으로 바꿔 실행한뒤 결과 타입 확인
    student= Student(name='하늘',age=23, interests=['AI','python'],nickname='a',student_id='23')
    print('학생',student)
    print('age 타입',type(student.age))
    print('dictionary 변환',student.model_dump())
    #age에 스물셋을 전달하고 validationError를 처리하는 코드 작성

if __name__=='__main__':
    main()



