@echo off
echo =======================================================================
echo              BCHAIN-ACCESS GITHUB DEPOSIT SCRIPT
echo =======================================================================
echo.
echo This script will:
echo   1. Initialize a local Git repository.
echo   2. Stage the codebase (excluding files in .gitignore).
echo   3. Create the initial commit.
echo   4. Link to remote: https://github.com/mallisami/Bchain_Access-
echo   5. Push the branch to main.
echo.
echo PREREQUISITES:
echo   - Git must be installed on your computer.
echo   - You must have write permissions to this repository.
echo   - You must be authenticated to GitHub on this machine.
echo.
set /p proceed="Do you want to initialize and push now? (Y/N): "
if /i "%proceed%" neq "Y" (
    echo Operation cancelled by user.
    pause
    exit /b
)

echo.
echo [1/5] Initializing local Git repository...
git init
if %ERRORLEVEL% neq 0 (
    echo Failed to initialize Git. Is Git installed on your system?
    pause
    exit /b
)

echo [2/5] Staging files...
git add .

echo [3/5] Committing changes...
git commit -m "Initialize BCHAIN-ACCESS framework prototype codebase for reproducibility and audit"

echo [4/5] Setting up remote repository...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/mallisami/Bchain_Access-
git branch -M main

echo [5/5] Pushing to GitHub...
echo.
git push -u origin main

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Push failed. 
    echo Please verify that:
    echo   1. You have created the repository 'Bchain_Access-' on GitHub.
    echo   2. You have write permissions to 'mallisami/Bchain_Access-'.
    echo   3. You have logged in to your GitHub account (Credential Helper, SSH, or token).
) else (
    echo.
    echo [SUCCESS] Codebase pushed successfully to https://github.com/mallisami/Bchain_Access-
)
echo.
pause
