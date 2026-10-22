# 요청 3개를 동시에 보내는경우
import asyncio
from time import perf_counter
import httpx

async def request_one(client, path, number):
    start = perf_counter()
    response = await client.get(path)
    response.raise_for_status()
    elapsed = perf_counter() - start    
    print(f'{path}요청 {number}: {response.status_code}, {elapsed:.2f}')
    return response.json()

async def compare(client,path):
    print(f'\n{path}: 요청 3개 시작')
    start = perf_counter()
    await asyncio.gather(
        request_one(client, path,1),
        request_one(client, path,2),
        request_one(client, path,3)
    )
    print(f'전체 완료 시간: {perf_counter() - start:.2f}초')

async def main():
    async with httpx.AsyncClient(
        base_url = "http://127.0.0.1:8000",
        timeout = 20.0,
        trust_env=False
    )as client:
        await compare(client,'/bad')
        await compare(client,'/good')

if __name__ == '__main__':
    asyncio.run(main())

#uvicorn Day7.main:app
#새터미널 만들기
#python Day7/probe.py