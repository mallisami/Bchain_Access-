@echo off
echo ===================================================
echo Recomputing data analysis metrics...
echo ===================================================
echo.
python experiments\scripts\compute_results.py
if %ERRORLEVEL% neq 0 (
    echo Failed to recompute statistical summaries.
    exit /b %ERRORLEVEL%
)

echo.
echo ===================================================
echo Re-running Hardhat tests...
echo ===================================================
echo.
cd experiments\hardhat
call npx hardhat test
if %ERRORLEVEL% neq 0 (
    cd ..\..
    exit /b %ERRORLEVEL%
)
cd ..\..

echo.
echo ===================================================
echo Re-running static security analysis (Slither)...
echo ===================================================
echo.
cd experiments\hardhat
slither . --json ..\..\results\slither-report.json > ..\..\results\slither-summary.txt 2>&1
if %ERRORLEVEL% neq 0 (
    echo Note: Slither completed (or exited with codes/warnings). Check results\slither-report.json for details.
) else (
    echo Slither static analysis run completed!
)
cd ..\..

echo.
echo Reproduction pipeline run completed!
