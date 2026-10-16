# 딕셔너리
# key_value 한쌍이 하나의 값

# 리스트 vs 딕셔너리
list_1=[10,20,30,[1,2,3]]
dict_1={'kor':80, 'eng': 80, 'math':90}

dict_1.keys()
dict_1.values()
dict_1.items()

for i in dict_1.items():
    print(i,i[0],i[1])

number1,number2=(10,20)
print(number1,number2)

for key,value in dict_1.items():
    print(f"key ={key}, value={value}")
