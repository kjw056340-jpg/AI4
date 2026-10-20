from pathlib import Path
import argparse
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def port_number(value):
    value = int(value)
    if not 1 <= value <= 65535:
        raise argparse.ArgumentTypeError('port must be between 1 and 65535')
    return value

def main():
    parser = argparse.ArgumentParser(description='Run a course lesson with Uvicorn.')
    parser.add_argument('lesson', type=int, choices=range(1, 9))
    parser.add_argument('--port', type=port_number, default=8000)
    args = parser.parse_args()
    import uvicorn
    name = f'labs.lesson{args.lesson:02}' + ('.main' if args.lesson == 8 else '')
    os.chdir(ROOT)
    print('Open http://127.0.0.1:' + str(args.port) + '/docs', flush=True)
    uvicorn.run(name + ':app', host='127.0.0.1', port=args.port, reload=False)

if __name__ == '__main__':
    main()
