@echo off
setlocal
cd /d "%~dp0.."
call "%~dp0python.cmd" -m pytest %*
exit /b %errorlevel%
