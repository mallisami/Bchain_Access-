@echo off
echo ===================================================
echo Running Hardhat contract unit tests...
echo ===================================================
echo.
cd experiments\hardhat
call npx hardhat test > ..\..\results\hardhat-test-output.txt 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo Hardhat tests failed. See results\hardhat-test-output.txt for details.
    type ..\..\results\hardhat-test-output.txt
    cd ..\..
    exit /b %ERRORLEVEL%
)
type ..\..\results\hardhat-test-output.txt
cd ..\..
echo.
echo Tests run completed successfully!
