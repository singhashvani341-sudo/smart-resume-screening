@echo off
title Smart Resume Screening

cd /d "%~dp0"

if not exist "app.py" (
    echo.
    echo ERROR: app.py not found.
    echo.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo.
    echo First-time setup detected.
    echo Creating virtual environment...
    echo.

    python -m venv venv

    if errorlevel 1 (
        echo.
        echo ERROR: Could not create the virtual environment.
        echo Make sure Python is installed and added to PATH.
        echo.
        pause
        exit /b 1
    )

    echo.
    echo Installing required packages...
    echo This may take several minutes.
    echo.

    "venv\Scripts\python.exe" -m pip install -r requirements.txt

    if errorlevel 1 (
        echo.
        echo ERROR: Package installation failed.
        echo Check the internet connection and try again.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Starting Smart Resume Screening...
echo Keep this window open while using the application.
echo.

"venv\Scripts\python.exe" -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo The application stopped because of an error.
    pause
)