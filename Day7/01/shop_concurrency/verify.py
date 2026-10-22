"""실제 단일 워커 서버로 동시성/상태 확인 지연을 검증합니다. 외부 네트워크 불필요."""

import asyncio
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent


async def check(base_url):
    async with httpx.AsyncClient(base_url=base_url, timeout=15, trust_env=False) as client:
        for _ in range(100):
            try:
                response = await client.get('/api/health')
                response.raise_for_status()
                break
            except httpx.TransportError:
                await asyncio.sleep(0.1)
        else:
            raise RuntimeError('검증 서버를 시작하지 못했습니다.')

        page = await client.get('/')
        assert page.status_code == 200 and '동시성 마켓' in page.text
        for asset in ('app.js', 'style.css'):
            assert (await client.get(f'/static/{asset}')).status_code == 200
        assert len((await client.get('/api/catalog')).json()) == 4
        assert (await client.get('/api/products/999')).status_code == 404
        assert (await client.get('/api/products/1?mode=invalid')).status_code == 422
        assert (await client.get('/api/products/1?delay=-1')).status_code == 422

        totals = {}
        health_times = {}
        for mode in ('blocking', 'async', 'thread'):
            async def detail(product_id):
                response = await client.get(f'/api/products/{product_id}?mode={mode}&delay=0.5')
                response.raise_for_status()
                assert response.json()['product']['id'] == product_id

            async def ping():
                await asyncio.sleep(0.15)
                start = time.perf_counter()
                response = await client.get('/api/health')
                response.raise_for_status()
                return time.perf_counter() - start

            start = time.perf_counter()
            results = await asyncio.gather(detail(1), detail(2), detail(3), ping())
            totals[mode] = time.perf_counter() - start
            health_times[mode] = results[-1]
            print(f'{mode:8}: total={totals[mode]:.2f}s, health={health_times[mode]:.2f}s')

        # 상대적인 차이를 검증하여 느린 PC에서도 절대 시간에 덜 의존합니다.
        assert totals['blocking'] > totals['async'] * 1.5, totals
        assert totals['blocking'] > totals['thread'] * 1.5, totals
        assert health_times['blocking'] > health_times['async'] + 0.5, health_times
        assert health_times['blocking'] > health_times['thread'] + 0.5, health_times
        print('PASS: 페이지, API 입력 검증, 세 방식의 동시성 및 상태 확인 지연')


if __name__ == '__main__':
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', str(port), '--workers', '1', '--log-level', 'warning'],
        cwd=ROOT,
    )
    try:
        asyncio.run(check(f'http://127.0.0.1:{port}'))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
