@echo off
echo ===================================================
echo Setting up BCHAIN-ACCESS local environments...
echo ===================================================
echo.
echo Installing Node.js dependencies for Hardhat...
cd experiments\hardhat
call npm install
if %ERRORLEVEL% neq 0 (
    echo Failed to install Node.js dependencies.
    exit /b %ERRORLEVEL%
)
cd ..\..

echo.
echo Setting up Python virtual environment...
cd core\backend
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Failed to create Python virtual environment.
    exit /b %ERRORLEVEL%
)
call venv\Scripts\activate
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install Python dependencies.
    exit /b %ERRORLEVEL%
)
cd ..\..

echo.
echo Setup completed successfully!
