import asyncio
import time
from time import perf_counter

async def make_drink(name):
    print(f'{name} 만들기 시작')
    #time.sleep(2)
    await asyncio.sleep(2)
    print(f'{name} 완성')
    return name

async def main():
    start=perf_counter()
    await make_drink('커피')
    await make_drink('차')
    print(f'순서대로 기다림 : {perf_counter()-start:.2f}초\n')

    start=perf_counter()
    result=await asyncio.gather(make_drink('커피'), make_drink('차'))
    print(f'함께 기다림 : {perf_counter()-start:.2f}초\n ')
    print('결과',result)

if __name__=='__main__':
    asyncio.run(main())
