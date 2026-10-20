"""Real subprocess + TCP tests, separate from in-process TestClient."""
from pathlib import Path
import json
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen
import pytest

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def wait_json(url, process, expected=None):
    deadline = time.monotonic() + 25
    last = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError(f'Uvicorn exited early: {process.returncode}')
        try:
            with urlopen(url, timeout=1) as r:
                value = json.load(r)
            if expected is None or value == expected:
                return value
        except (OSError, ValueError) as exc:
            last = exc
        time.sleep(.15)
    raise AssertionError(f'Server did not become ready: {last}')


@pytest.mark.parametrize('number', range(1, 9))
def test_real_uvicorn(number):
    module = f'labs.lesson{number:02}' + ('.main' if number == 8 else '')
    port = free_port()
    with tempfile.TemporaryFile(mode='w+b') as log:
        process = subprocess.Popen([sys.executable, '-m', 'uvicorn', module + ':app',
            '--host', '127.0.0.1', '--port', str(port)], cwd=ROOT,
            stdout=log, stderr=log)
        try:
            result = wait_json(f'http://127.0.0.1:{port}/openapi.json', process)
            assert result['paths']
        finally:
            process.terminate()
            process.wait(timeout=10)

