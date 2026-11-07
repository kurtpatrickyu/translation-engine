@echo off
setlocal
set "ENGINE_PYTHON=%~dp0..\.venv\Scripts\python.exe"
if not exist "%ENGINE_PYTHON%" (
  echo Missing project .venv. Run scripts\setup.cmd with CPython 3.12.10 x64 first. 1>&2
  exit /b 2
)
"%ENGINE_PYTHON%" %*
exit /b %errorlevel%
