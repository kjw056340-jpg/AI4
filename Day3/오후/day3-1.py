names = ['홍길도','이순신','강감찬']

#id=1
#for name in names:
#    print(f'{id}.{name}')
#    id+=1

#for id,name in enumerate(names,start=1):
#    print(id,name)

raw_logs = [
    "epoch=1,loss=0.45,acc=88.5",
    "epoch=2,loss=invalid,acc=91.0",   # ValueError 발생 라인 ('invalid'는 float 변환 불가)   
    "epoch=3,loss=0.31",               # KeyError 발생 라인 ('acc' 키 누락)    
    "epoch=4,loss=0.22,acc=94.2",]

#test_str = ['epoch=1,loss=0.45,acc=88.5']

for line in raw_logs:
    parts=dict(item.split('=') for item in line.split(','))
    try:
        record = {
                "epoch": int(parts["epoch"]),
                "loss": float(parts["loss"]),
                "acc": float(parts["acc"]),
            }
        print (record)
    except ValueError as e:
        print('값이 잘못되었습니다', e)
    except KeyError as e:
        print('키캆을 확인하세요',e)


