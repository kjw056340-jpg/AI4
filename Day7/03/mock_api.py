import asyncio
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse, PlainTextResponse, Response

app = FastAPI()
active = 0
peak = 0
attempts = {}


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.get('/items/{item_id}')
async def item(item_id: int):
    # 번호별 대기 시간을 달리해 완료 순서를 바꿉니다.
    await asyncio.sleep({1: 0.6, 2: 0.1, 3: 0.3}.get(item_id, 0.1))
    return {'id': item_id, 'title': f'할 일 {item_id}', 'completed': False}


@app.get('/cases/{case}')
async def case_response(case: str):
    data = {'id': 1, 'title': '실습 준비', 'completed': False}
    if case == 'slow':
        await asyncio.sleep(0.6)
    if case == 'missing':
        data.pop('title')
    if case == 'wrong_bool':
        data['completed'] = 'false'
    if case == 'list':
        return [data]
    if case == 'html':
        return PlainTextResponse('<html>점검 중</html>', media_type='text/html')
    if case == 'broken_json':
        return Response(content='{"id":', media_type='application/json')
    if case == 'not_found':
        return JSONResponse(status_code=404, content={'message': '없음'})
    if case == 'server_error':
        return JSONResponse(status_code=503, content={'message': '잠시 후 재시도'})
    return data


@app.get('/limited/{item_id}')
async def limited(item_id: int):
    global active, peak
    if active >= 2:
        return JSONResponse(status_code=429, content={'message': '동시 요청 초과'})
    active += 1
    peak = max(peak, active)
    try:
        await asyncio.sleep(0.15)
        return {'id': item_id, 'title': f'할 일 {item_id}', 'completed': False}
    finally:
        # 취소나 예외가 나도 사용 중인 자리 수를 돌려놓습니다.
        active -= 1


@app.get('/metrics')
async def metrics():
    return {'active': active, 'peak': peak}


@app.get('/flaky/{item_id}')
async def flaky(item_id: int, x_request_id: str = Header(default='demo')):
    key = (x_request_id, item_id)
    attempts[key] = attempts.get(key, 0) + 1
    count = attempts[key]
    # 같은 작업 식별자로 호출하면 처음 두 번 실패, 세 번째부터 성공.
    if count <= 2:
        return JSONResponse(status_code=503, content={'attempt': count})
    return {'id': item_id, 'attempt': count, 'title': '재시도 성공'}


@app.get('/tools/{name}')
async def tool(name: str, scenario: str = 'normal'):
    if scenario == 'all_fail':
        return JSONResponse(status_code=503, content={'message': '도구 점검'})
    if scenario == 'partial' and name == 'schedule':
        await asyncio.sleep(0.7)
    if scenario == 'partial' and name == 'news':
        return JSONResponse(status_code=503, content={'message': '뉴스 점검'})
    await asyncio.sleep(0.05)
    return {'tool': name, 'text': f'{name} 도구에서 확인한 학습용 정보'}

#uvicorn mock_api:app  --reload --port 9000