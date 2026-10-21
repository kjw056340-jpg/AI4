"""05장 학생 실습: 강좌와 수강생의 중첩 관계 모델링."""
from pydantic import BaseModel,Field


# TODO 1: Learner(name:str, score:int 0~100)
class Learner(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)


# TODO 2: Course(title:str, learners:list[Learner] 최소 1명)
class Course(BaseModel):
    title: str
    learners: list[Learner]=Field(min_length=1)


def main() -> None:
    print('TODO: dict 데이터를 중첩 모델로 검증하세요.')


if __name__ == '__main__':
    main()
