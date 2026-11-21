@echo off
setlocal
set "skill_env=%LOCALAPPDATA%\kobe-agent-kit\windows-computer-use\venv"
set "skill_python=%skill_env%\Scripts\python.exe"
if exist "%skill_python%" goto install
where py.exe >nul 2>&1
if errorlevel 1 goto use_python
py -3 -m venv "%skill_env%"
if errorlevel 1 exit /b 1
goto install

:use_python
python.exe -m venv "%skill_env%"
if errorlevel 1 exit /b 1

:install
"%skill_python%" -m pip install -r "%~dp0scripts\requirements.txt"
if errorlevel 1 exit /b 1
"%skill_python%" "%~dp0scripts\desktop.py" doctor
exit /b %errorlevel%
