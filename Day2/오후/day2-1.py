list_1=['a','b','c']
list_2=[100,200,300]
result= list(zip(list_1, list_2))
for i in result:
    print(i)


# zip을 생성한 객체를 dictionary 변환
result = dict(result)
print(result)


