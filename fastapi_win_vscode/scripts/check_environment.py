from pathlib import Path
from importlib import metadata, import_module
import platform
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    errors = []
    print('Project:', ROOT)
    print('Python:', sys.executable)
    print('Version:', platform.python_version())
    if sys.version_info[:2] not in {(3, 12), (3, 13)}:
        errors.append('Expected Python 3.12 or 3.13.')
    if Path(sys.prefix).resolve() != (ROOT / '.venv').resolve():
        errors.append('Run with .venv\\Scripts\\python.exe, not global Python.')
    for line in (ROOT / 'requirements.txt').read_text(encoding='utf-8-sig').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        name, expected = line.split('==', 1)
        try:
            actual = metadata.version(name)
            if actual != expected:
                errors.append(f'{name}: expected {expected}, found {actual}')
        except metadata.PackageNotFoundError:
            errors.append(f'Missing package: {name}')
    if not errors:
        for number in range(1, 9):
            name = f'labs.lesson{number:02}' + ('.main' if number == 8 else '')
            try:
                assert import_module(name).app
            except Exception as error:
                errors.append(f'{name}: {error}')
    for error in errors:
        print('FAIL:', error)
    print('ENVIRONMENT OK' if not errors else 'ENVIRONMENT FAILED')
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
