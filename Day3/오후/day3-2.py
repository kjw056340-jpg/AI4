class promptEmptyError(Exception):
    pass

prompt= ""
try:
    print(1/0)

    if not prompt.strip():
        raise promptEmptyError()
    

except Exception as e:
    print('프롬프트는 반드시 제공되어야 합니다.')
except ZeroDivisionError as e:
    print('0으로 나눌 수 없습니다.')

print('정상종료')
