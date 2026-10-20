"""Run lesson 8 in another terminal first. Uses only the standard library."""
import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    base = f'http://127.0.0.1:{args.port}'

    def request(method, path, expected, body=None):
        payload = json.dumps(body).encode('utf-8') if body is not None else None
        req = Request(base + path, data=payload, method=method,
                      headers={'Content-Type': 'application/json'})
        try:
            response = urlopen(req, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            status, raw = response.code, response.read()
        assert status == expected, (method, path, status, raw)
        data = json.loads(raw) if raw else None
        print(method, path, '->', status, data)
        return data

    request('GET', '/health', 200)
    task = request('POST', '/tasks', 201, {'title': 'Windows VS Code task'})
    path = '/tasks/' + str(task['id'])
    request('GET', path, 200)
    assert request('PATCH', path, 200, {'done': True})['done'] is True
    assert request('PUT', path, 200, {'title': 'Replaced'})['done'] is False
    request('DELETE', path, 204)
    request('GET', path, 404)
    request('POST', '/tasks', 422, {'title': '   '})
    request('POST', '/health', 405)
    print('HTTP WALKTHROUGH OK')

if __name__ == '__main__':
    main()
