import asyncio
import os
import sys
import httpx

BASE_URL = "https://jsonplaceholder.typicode.com"

async def main(todo_id):
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=10.0
    )as client:
        response = await client.get(f"/posts/{todo_id}")
        print(response, type(response),response.json())
        jsondata=response.json()
        print('\n\n',jsondata['title'])

if __name__=='__main__':
    asyncio.run( main(1) )

#python 01.fetch.py