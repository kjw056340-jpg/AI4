# 실습 후 비교·자기 점검

## 최소 수정

apply_changes에서 UPDATE 뒤, DELETE 앞의 다음 한 줄을 제거한다.

```python
connection.commit()  # 두 작업 사이의 확정 시점을 관찰한다.
```

prepare_database의 commit과 두 작업 성공 뒤의 commit은 그대로 둔다.
삭제 id가 없으면 DELETE 자체는 0행에 적용되고 SQL 오류는 발생하지 않는다.
이 수업의 '정확히 1명 삭제' 약속에 따라 rowcount를 검사해서 Python ValueError를 발생시킨다.
기존 코드는 그 전에 점수 변경을 확정해서 rollback이 이전 트랜잭션까지 되돌리지 못했다.
중간 commit을 제거하면 UPDATE와 DELETE가 같은 트랜잭션에 남고 실패 시 함께 취소된다.

| 상황 | 기대 상태 |
| --- | --- |
| id=1을 90점·id=3 삭제 성공 | 민지 90·준호 95 |
| 삭제 id=999 없음 | 원본 민지 80·준호 95·수아 70 |
| 수정 id=999 없음 | 원본 세 행 |
| points=None | NOT NULL 오류, 원본 세 행 |
| points=0 | 민지 0·준호 95 |

## 확인 질문 답

1. UPDATE는 기존 행의 값을 바꾸고 DELETE는 행을 제거한다. DELETE는 테이블 자체를 지우는 명령이 아니다.
2. WHERE를 생략하면 전체 행이 수정·삭제 대상이다. UPDATE의 SET 값은 바꿀 내용이고 WHERE는 대상이다.
3. rowcount는 해당 문장의 영향 행 수다. 이 실습의 id PK 조건은 0 또는 1행에 일치한다.
4. 없는 id의 UPDATE·DELETE는 보통 0행이며 SQL 오류가 아니다. 정확히 한 행이어야 한다는 검사는 앱의 정책이다.
5. commit은 현재 트랜잭션의 변경 확정이고 rollback은 아직 확정하지 않은 변경을 취소한다.
6. commit한 이전 변경은 나중의 rollback으로 되돌릴 수 없다.
7. 샘플 준비를 끝내는 commit은 업무 변경을 시작하기 전에 원본 데이터를 확정한다.
8. 같은 연결의 조회만으로 저장 상태를 판단하지 않는다. 작업 종료 뒤 새 연결의 전체 행을 비교한다.
9. 트랜잭션은 서로 관련된 작업을 성공·실패 단위로 묶는다. 이 실습은 점수 수정과 사용자 삭제를 한 묶음으로 약속했다.
10. 각 실행은 별도 임시 DB를 만들고 종료 때 정리한다. 기존 practice.db·lesson02.db는 사용하지 않는다.

## 제출 평가 — 10점

- UPDATE·DELETE·WHERE·영향 행 수 설명: 2점
- commit 경계와 부분 저장 원인 설명: 3점
- 중간 commit 한 줄 제거·정상 및 실패 여섯 검사 통과: 3점
- WHERE 누락 3행 영향·rollback 원복 결과와 새 연결 비교: 2점

제출: 수정 main.py, check.py의 전후 출력, reproduce.py 결과, 원인 설명.
