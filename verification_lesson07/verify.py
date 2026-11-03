"""Synthetic-only verification; never reads the project's .env or original DB."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import socket
import sqlite3
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'Day14' / 'main7.py'
DOC = ROOT.parent / 'Day14' / 'readme7.md'
PACKAGES = ROOT.parent / 'Day14' / 'venv' / 'Lib' / 'site-packages'
sys.path.insert(0, str(PACKAGES))
import redis

before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE, DOC)}
spec = importlib.util.spec_from_file_location('lesson07_under_test', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
results = []

def check(name, kind, fn):
    try:
        detail = fn()
        results.append(dict(test=name, kind=kind, status='PASS', detail=detail or ''))
    except Exception as exc:
        # Do not serialize exception text, connection values, captured stdout or identifiers.
        results.append(dict(test=name, kind=kind, status='FAIL', detail=type(exc).__name__))
    print(results[-1]['status'] + ' | ' + kind + ' | ' + name, flush=True)

def require(value):
    if not value:
        raise AssertionError('verification failed')

def quiet(fn, *args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        value = fn(*args)
    return value, out.getvalue()

class Cache:
    def __init__(self, get_error=False, set_error=False, delete_error=False):
        self.data = {}
        self.calls = []
        self.get_error, self.set_error, self.delete_error = get_error, set_error, delete_error
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def get(self, key):
        self.calls.append('GET')
        if self.get_error: raise redis.exceptions.ConnectionError('synthetic')
        return self.data.get(key)
    def set(self, key, value, **kwargs):
        self.calls.append('SET')
        if self.set_error: raise redis.exceptions.ConnectionError('synthetic')
        self.data[key] = value
        return True
    def delete(self, key):
        self.calls.append('DEL')
        if self.delete_error: raise redis.exceptions.ConnectionError('synthetic')
        return int(self.data.pop(key, None) is not None)

def cli(args, cache=None):
    out = io.StringIO()
    with patch.object(sys, 'argv', [str(SOURCE), *args]), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        cm = patch.object(redis, 'Redis', return_value=cache) if cache is not None else contextlib.nullcontext()
        with cm:
            try:
                runpy.run_path(str(SOURCE), run_name='__main__')
                code = 0
            except SystemExit as exc:
                code = exc.code
    return code, out.getvalue()

with tempfile.TemporaryDirectory(prefix='synthetic-', dir=ROOT) as tmp:
    tmp = Path(tmp)
    db = tmp / 'source.sqlite'
    # A bound but non-listening loopback socket reserves a TCP endpoint which refuses connections.
    # This is genuine socket I/O, but does not claim a running Redis was stopped.
    with socket.socket() as unavailable:
        unavailable.bind(('127.0.0.1', 0))
        port = unavailable.getsockname()[1]
        def refused():
            with socket.socket() as probe:
                probe.settimeout(3)
                require(probe.connect_ex(('127.0.0.1', port)) == 10061)
        check('TCP endpoint explicitly refuses connection (Windows 10061)', 'real TCP refusal', refused)
        env = {k: os.environ[k] for k in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP') if k in os.environ}
        env.update(REDIS_HOST='127.0.0.1', REDIS_PORT=str(port), SQLITE_PATH=str(db),
                   PYTHONPATH=str(PACKAGES), PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
        def network_cli(args):
            p = subprocess.run([sys.executable, str(SOURCE), *args], cwd=tmp, env=env,
                               capture_output=True, encoding='utf-8', timeout=45)
            return p.returncode, p.stdout + p.stderr
        def init():
            code, out = network_cli(['init'])
            require(code == 0 and '원본 준비 완료' in out)
        check('isolated CLI init', 'local SQLite', init)
        def net_history():
            code, out = network_cli(['history', 'demo-a'])
            require(code == 0 and '조회 경로: BYPASS' in out and '캐시 읽기 실패' in out)
        check('unavailable endpoint: history BYPASS exit 0', 'real TCP refusal', net_history)
        def net_session():
            code, out = network_cli(['session', 'sid_SYNTHETIC_NOT_ISSUED'])
            require(code == 1 and '세션 확인 불가' in out and '접근을 거절' in out and '세션 사용자:' not in out)
        check('unavailable endpoint: session denied exit 1', 'real TCP refusal', net_session)
        def net_add():
            with contextlib.closing(sqlite3.connect(db)) as conn:
                n = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
                old = m.cache_key(conn, 'demo-a')
            code, out = network_cli(['add', 'demo-a', 'SYNTHETIC_OUTAGE_MESSAGE'])
            with contextlib.closing(sqlite3.connect(db)) as conn:
                rows = conn.execute('SELECT role, content FROM messages ORDER BY id').fetchall()
                require(len(rows) == n + 2 and rows[-2:] == [('user', 'SYNTHETIC_OUTAGE_MESSAGE'), ('assistant', '모의 응답: SYNTHETIC_OUTAGE_MESSAGE')])
                require(old != m.cache_key(conn, 'demo-a'))
            require(code == 0 and '원본 저장 완료: 2개 메시지' in out and '이전 캐시 삭제 실패' in out)
            code, out = network_cli(['history', 'demo-a'])
            require(code == 0 and '조회 경로: BYPASS' in out and 'SYNTHETIC_OUTAGE_MESSAGE' in out)
            return 'Two rows verified through a fresh SQLite connection; subsequent history includes both.'
        check('unavailable endpoint: add commits two rows and warns on DEL', 'real TCP refusal', net_add)

    previous = Path.cwd()
    os.chdir(tmp)
    with patch.dict(os.environ, env, clear=True), contextlib.closing(sqlite3.connect(db)) as conn:
        def write_fail():
            c = Cache(set_error=True)
            (rows, route), out = quiet(m.load_history, conn, c, 'demo-a')
            require(route == 'MISS_WRITE_FAILED' and rows == m.read_source(conn, 'demo-a'))
            require(c.calls == ['GET', 'SET'] and '캐시 저장 실패' in out)
            code, out = cli(['history', 'demo-a'], Cache(set_error=True))
            require(code == 0 and 'MISS_WRITE_FAILED' in out and 'BYPASS' not in out)
            return 'GET returned nil normally; only SET raised. Source rows returned, exit 0.'
        check('GET succeeds, SET alone fails', 'fault injection', write_fail)
        def cache_hit():
            c = Cache(set_error=True)
            c.data[m.cache_key(conn, 'demo-a')] = json.dumps(m.read_source(conn, 'demo-a'))
            (rows, route), _ = quiet(m.load_history, conn, c, 'demo-a')
            require(route == 'HIT' and c.calls == ['GET'])
        check('valid cache HIT does not call SET', 'fault injection control', cache_hit)
        def source_version_failure():
            broken = tmp / 'missing_table.sqlite'
            sqlite3.connect(broken).close()
            c = Cache()
            c.data['synthetic'] = '[{"role":"user","content":"SYNTHETIC"}]'
            with patch.dict(os.environ, {'SQLITE_PATH': str(broken)}):
                code, out = cli(['history', 'demo-a'], c)
            require(code == 1 and '원본 DB 오류:' in out and '조회 경로:' not in out and c.calls == [])
            return 'Version query fails before GET; no successful cache result is emitted.'
        check('SQLite version lookup failure is not hidden by cache', 'local SQLite error + cache spy', source_version_failure)
        def source_read_failure(get_error):
            c = Cache(get_error=get_error)
            with patch.object(m, 'read_source', side_effect=sqlite3.OperationalError('synthetic')):
                try:
                    quiet(m.load_history, conn, c, 'demo-a')
                except sqlite3.OperationalError:
                    require(c.calls == ['GET'])
                    return
                raise AssertionError()
        check('SQLite read failure after successful GET miss propagates', 'fault injection', lambda: source_read_failure(False))
        check('SQLite read failure on BYPASS propagates', 'fault injection', lambda: source_read_failure(True))
        def stale_key():
            c = Cache(delete_error=True)
            old = m.cache_key(conn, 'demo-a')
            c.data[old] = json.dumps(m.read_source(conn, 'demo-a'))
            quiet(m.save_turn, conn, 'demo-a', 'SYNTHETIC_NEW', 'SYNTHETIC_REPLY')
            _, out = quiet(m.invalidate, c, old)
            (rows, route), _ = quiet(m.load_history, conn, c, 'demo-a')
            require('이전 캐시 삭제 실패' in out and old in c.data and old != m.cache_key(conn, 'demo-a'))
            require(route == 'MISS' and rows[-1]['content'] == 'SYNTHETIC_REPLY')
        check('DEL failure leaves old cache but new version selects fresh rows', 'fault injection', stale_key)
        def rollback():
            n = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
            conn.execute("CREATE TEMP TRIGGER reject_assistant BEFORE INSERT ON messages WHEN NEW.role='assistant' BEGIN SELECT RAISE(ABORT, 'synthetic'); END")
            try:
                quiet(m.save_turn, conn, 'demo-a', 'SYNTHETIC_ROLLBACK', 'SYNTHETIC_REPLY')
            except sqlite3.IntegrityError:
                require(conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0] == n)
            else:
                raise AssertionError()
            finally:
                conn.execute('DROP TRIGGER reject_assistant')
        check('second INSERT failure rolls back both messages', 'SQLite trigger fault injection', rollback)
        for label, c in [('GET failure', Cache(get_error=True)), ('missing session', Cache())]:
            def denied(c=c):
                code, out = cli(['session', 'sid_SYNTHETIC_NOT_ISSUED'], c)
                require(code == 1 and '접근을 거절' in out and '세션 사용자:' not in out)
            check('session denied: ' + label, 'fault injection', denied)
    os.chdir(previous)

after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE, DOC)}
check('original source and lesson document unchanged', 'SHA-256 comparison', lambda: require(before == after))
report = {
    'target': 'Day14/main7.py and Day14/readme7.md (user confirmed)',
    'runtime': {'python': sys.version.split()[0], 'redis_py': redis.__version__, 'sqlite': sqlite3.sqlite_version},
    'results': results,
    'limitations': [
        'No actual Redis server stop/restart was tested: no available Redis/Docker executable was found.',
        'Real TCP tests use a reserved, non-listening loopback endpoint, not a mocked Redis client.',
        'The network session identifier was synthetic and never issued; no pre-outage valid-session lifecycle is claimed.',
        'No web authentication, actual accounts, external endpoints, project .env or original SQLite data were used.',
    ],
}
(ROOT / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
for r in results:
    print(r['status'] + ' | ' + r['kind'] + ' | ' + r['test'])
print(f"TOTAL {sum(r['status']=='PASS' for r in results)}/{len(results)}")
raise SystemExit(any(r['status'] != 'PASS' for r in results))
