import importlib
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(request):
    number = request.param
    name = f"labs.lesson{number:02}"
    if number == 8:
        import labs.lesson08.store as store
        importlib.reload(store)
        name += ".main"
    module = importlib.reload(importlib.import_module(name))
    with TestClient(module.app) as c:
        yield c


@pytest.mark.parametrize("client", range(1, 9), indirect=True)
def test_docs_and_schema(client):
    assert client.get('/docs').status_code == 200
    assert client.get('/openapi.json').json()['openapi'].startswith('3.')


@pytest.mark.parametrize("client", [1], indirect=True)
def test_hello(client):
    assert client.get('/').json() == {'message': 'Hello FastAPI'}


@pytest.mark.parametrize("client", [2], indirect=True)
def test_method_dispatch(client):
    assert client.get('/method').json()['method'] == 'GET'
    r = client.post('/method')
    assert r.status_code == 201 and r.json()['method'] == 'POST'
    assert client.delete('/method').status_code == 405
    assert client.get('/missing').status_code == 404


@pytest.mark.parametrize("client", [3], indirect=True)
def test_paths_and_order(client):
    assert client.get('/tasks/stats').json() == {'total': 1}
    assert client.get('/tasks/1').json()['id'] == 1
    assert client.get('/tasks/99').status_code == 404
    assert client.get('/tasks/abc').status_code == 422
    assert client.get('/tasks/0').status_code == 422


@pytest.mark.parametrize("client", [4], indirect=True)
def test_query(client):
    assert client.get('/tasks').json()['total'] == 3
    assert client.get('/tasks?q=FASTapi').json()['items'][0]['id'] == 1
    assert client.get('/tasks?done=false&skip=1&limit=1').json() == {
        'items': [{'id': 3, 'title': 'Python review', 'done': False}], 'total': 2}
    assert client.get('/tasks?q=not-present').json() == {'items': [], 'total': 0}


@pytest.mark.parametrize("client", [4, 8], indirect=True)
@pytest.mark.parametrize("query", ['skip=-1', 'limit=0', 'limit=21', 'done=maybe'])
def test_bad_query(client, query):
    assert client.get('/tasks?' + query).status_code == 422


@pytest.mark.parametrize("client", [5, 6, 7, 8], indirect=True)
def test_create_and_read(client):
    r = client.post('/tasks', json={'title': '  New task  '})
    assert r.status_code == 201
    assert r.json() == {'id': 2, 'title': 'New task', 'done': False}
    assert client.get('/tasks/2').json() == r.json()
    assert client.get('/tasks/99').status_code == 404


@pytest.mark.parametrize("client", [5, 6, 7, 8], indirect=True)
@pytest.mark.parametrize("body", [{}, {'title': ''}, {'title': '   '},
    {'title': 'x' * 81}, {'title': 'x', 'done': 'false'},
    {'title': 'x', 'id': 55}, {'title': None}])
def test_invalid_body(client, body):
    assert client.post('/tasks', json=body).status_code == 422
    r = client.get('/tasks').json()
    rows = r['items'] if isinstance(r, dict) else r
    assert len(rows) == 1


@pytest.mark.parametrize("client", [6, 7, 8], indirect=True)
def test_put_patch_semantics(client):
    assert client.patch('/tasks/1', json={'done': True}).json()['title'] == 'FastAPI basics'
    r = client.put('/tasks/1', json={'title': 'Replaced'})
    assert r.status_code == 200
    assert r.json() == {'id': 1, 'title': 'Replaced', 'done': False}
    assert client.patch('/tasks/1', json={'done': True}).json()['done'] is True
    assert client.patch('/tasks/1', json={'title': 'Changed'}).json()['done'] is True
    assert client.put('/tasks/1', json={'done': True}).status_code == 422
    assert client.put('/tasks/99', json={'title': 'No'}).status_code == 404
    assert client.patch('/tasks/99', json={'done': True}).status_code == 404


@pytest.mark.parametrize("client", [6, 7, 8], indirect=True)
@pytest.mark.parametrize("body", [{}, {'title': None}, {'done': None},
    {'title': '   '}, {'done': 'false'}, {'unknown': 1}])
def test_invalid_patch(client, body):
    assert client.patch('/tasks/1', json=body).status_code == 422
    assert client.get('/tasks/1').json()['title'] == 'FastAPI basics'


@pytest.mark.parametrize("client", [7, 8], indirect=True)
def test_delete_and_id_reuse(client):
    assert client.post('/tasks', json={'title': 'Delete me'}).json()['id'] == 2
    r = client.delete('/tasks/2')
    assert r.status_code == 204 and r.content == b''
    assert client.get('/tasks/2').status_code == 404
    assert client.delete('/tasks/2').status_code == 404
    assert client.post('/tasks', json={'title': 'Next'}).json()['id'] == 3


@pytest.mark.parametrize("client", [8], indirect=True)
def test_final_filters_and_openapi(client):
    assert client.get('/health').json() == {'status': 'ok'}
    client.post('/tasks', json={'title': 'Python', 'done': True})
    client.post('/tasks', json={'title': 'FastAPI routing'})
    assert client.get('/tasks?q=FastAPI&done=false&skip=1&limit=1').json() == {
        'items': [{'id': 3, 'title': 'FastAPI routing', 'done': False}], 'total': 2}
    schema = client.get('/openapi.json').json()
    assert {'get', 'post'} <= schema['paths']['/tasks'].keys()
    assert {'get', 'put', 'patch', 'delete'} <= schema['paths']['/tasks/{task_id}'].keys()
    assert client.post('/health').status_code == 405


@pytest.mark.parametrize("client", [5, 6, 7, 8], indirect=True)
def test_malformed_json(client):
    assert client.post('/tasks', content='{', headers={
        'Content-Type': 'application/json'}).status_code == 422
