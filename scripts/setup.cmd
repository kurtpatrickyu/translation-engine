@echo off
setlocal
cd /d "%~dp0.."
if not exist requirements-dev.lock (
  echo Missing requirements-dev.lock. Restore the reviewed lock before setup. 1>&2
  exit /b 2
)
if exist .venv\Scripts\python.exe goto install
set "ENGINE_BOOTSTRAP_PYTHON=python"
if not "%~1"=="" set "ENGINE_BOOTSTRAP_PYTHON=%~1"
"%ENGINE_BOOTSTRAP_PYTHON%" -c "import sys,struct; assert sys.version_info[:3] == (3,12,10) and struct.calcsize('P') == 8, 'Use CPython 3.12.10 x64'"
if errorlevel 1 exit /b 2
"%ENGINE_BOOTSTRAP_PYTHON%" -m venv .venv
if errorlevel 1 exit /b 2
:install
.venv\Scripts\python.exe -c "import sys,struct; assert sys.version_info[:3] == (3,12,10) and struct.calcsize('P') == 8, 'Recreate .venv with CPython 3.12.10 x64'"
if errorlevel 1 exit /b 2
.venv\Scripts\python.exe scripts\setup_environment.py
exit /b %errorlevel%
