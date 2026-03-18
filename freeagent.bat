@echo off
setlocal
:: Get the directory where this batch file is located
set "BASE_DIR=%~dp0"
:: Path to the virtual environment python
set "PYTHON_EXE=%BASE_DIR%.venv\Scripts\python.exe"
:: Path to the main script
set "SCRIPT_PATH=%BASE_DIR%freeagent.py"

if not exist "%PYTHON_EXE%" (
    echo Error: Virtual environment not found at %BASE_DIR%.venv
    echo Please run 'python -m venv .venv' and 'pip install -r requirements.txt' first.
    exit /b 1
)

"%PYTHON_EXE%" "%SCRIPT_PATH%" %*
endlocal
