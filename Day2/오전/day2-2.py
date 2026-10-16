#논리연산자
isSuccess = True
isPass = False

if isSuccess and isPass:
    print('A')
else:
    print('B') 

#True and False => False
#True and True => True
#False and False => False
#False and True => False

if isSuccess or isPass:
    print('A')
else:
    print('B')   

#True or False => True
#True or True => True   
#False or False => False     
#False or True => True


#단락평가 Short-circuit
def expensive_check():
    print("시간이 오래 걸리는 함수 실행")
    return True

is_active = False

if is_active and expensive_check():
    print('통과')
else:
    print('차단 (expensive_check 실행 안됨)')


#None 값을 방어
user_profile = None
if use_profile is not None and user_profile.get('is_verified'):
    print('인증된 사용자')
else:
    print('비인증된 사용자')