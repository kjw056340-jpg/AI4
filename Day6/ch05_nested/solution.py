from pydantic import BaseModel, Field, ValidationError


class Learner(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)


class Course(BaseModel):
    title: str
    learners: list[Learner] = Field(min_length=1)


def main() -> None:
    course = Course.model_validate({
        'title': 'Pydantic 기초', 'learners': [{'name': '김학생', 'score': 92}]
    })
    print(course.learners[0].name)
    try:
        Course(title='Pydantic', learners=[{'name': '이학생', 'score': 120}])
    except ValidationError as error:
        print('중첩 오류:', error.errors()[0]['loc'])
    print('05장 정답 실행 성공')


if __name__ == '__main__':
    main()
