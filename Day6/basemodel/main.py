import Day6.basemodel.day6_2 as day6_2

member=day6_2.Member(username='홍길동',age=20,active =True,nickname=None)
if member.age>19:
    print('성인입니다')

print('main.py',__name__)