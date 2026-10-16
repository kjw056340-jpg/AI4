names = ['홍길도','이순신','강감찬']

#id=1
#for name in names:
#    print(f'{id}.{name}')
#    id+=1

#for id,name in enumerate(names,start=1):
#    print(id,name)


test_str = ['epoch=1,loss=0.45,acc=88.5']
for line in test_str:
    result=dict(item.split('=') for item in line.split(','))

    print (result)

