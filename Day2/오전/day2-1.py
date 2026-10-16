# if - elif - else
score= int(input('점수 : '))
if score >=90:
    print('A')
elif score >=80:
    print('B')
elif score>=70:
    print('C')
else:
    print('F')

#가독성X
if score >=90:
    print('A')
else:
    if score >=80:
        print('B')
    else:
        if score >=70:
            print('C')
        else:
            print('D')

#파일 이동
#cd Day2
#python Day2\day2-1.py