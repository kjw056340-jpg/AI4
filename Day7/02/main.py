import os
import httpx
from fastapi import FastAPI, HTTPException

BASE_URL = "https://jsonplaceholder.typicode.com"


app=FastAPI()

async def fetch_todo(todo_id):
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=10.0,
    ) as client:
        response= await client.get('f/todos/{todo_id}')
        print(response.status_code)
        return response.json()

@app.get('/todos/{todo_id}')
async def read_todo(todo_id:int):
    try:
        data =await fetch_todo(todo_id)
    except httpx.HTTPStatusError as e:
        print(e.response.status_code)
    return {
        "id": data.get('id',todo_id),
        'title': data.get('title','제목 없음'),
        'completed':data.get('completed',False)
    }


    
