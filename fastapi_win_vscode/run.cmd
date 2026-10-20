@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Missing .venv. Create it with: python -m venv .venv
  exit /b 1
)
".venv\Scripts\python.exe" scripts\run_lesson.py %*
exit /b %ERRORLEVEL%
