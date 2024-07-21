@echo off

:: Check if virtual environment directory exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

:: Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Install dependencies
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found.
)

:: Run the main file
if exist "jarvix\main.py" (
    echo Running main file...
    python -m jarvix.main
) else (
    echo Main file not found. Ensure jarvix\main.py exists.
)

:: Deactivate virtual environment
echo Deactivating virtual environment...
deactivate
