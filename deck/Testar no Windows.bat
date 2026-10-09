@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 server.py --autoteste
) else (
  python server.py --autoteste
)
pause
