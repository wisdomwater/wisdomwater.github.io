:: Automation script front-end for Windows
@echo off

setlocal

set venv=.venv
set pyexe=%venv%\Scripts\python.exe
set activate=%venv%\Scripts\activate.bat

:setup
    if "%~1" neq "setup" goto end_setup
    echo Setting up virtual environment
    if not exist %venv% python -m venv %venv%
    if not exist %venv% exit /b 1
    echo Activating the virtual environment
    call %activate% || exit /b 1
    echo Installing python packages
    pip install -r requirements.txt || exit /b 1
    echo Environment set up
    exit /b 0
:end_setup

call %activate%

:raw_cmd
    if "%~1" neq "--" goto end_raw_cmd
    set "args=%*"
    %args:~3%
    exit /b %errorlevel%
:end_raw_cmd

python scripts\do.py %*
