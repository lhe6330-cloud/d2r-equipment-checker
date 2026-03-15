@echo off
echo ========================================
echo D2R Equipment Checker - Build Script
echo ========================================
echo.

cd /d "%~dp0"
echo Working directory: %CD%
echo.

REM Check if Python is installed
py --version
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo.
echo [1/4] Installing dependencies...
py -m pip install PySide6 requests beautifulsoup4 pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Checking files exist...
if not exist "d2rcheck.py" (
    echo ERROR: d2rcheck.py not found!
    pause
    exit /b 1
)
if not exist "d2rcheck.ui" (
    echo ERROR: d2rcheck.ui not found!
    pause
    exit /b 1
)
echo All files found.

echo.
echo [3/4] Building executable (this takes 2-3 minutes)...
echo.
py -m PyInstaller --noconfirm --onefile --windowed --name "D2R_Equipment_Checker" --add-data "d2rcheck.ui;." --hidden-import "PySide6.QtCore" --hidden-import "PySide6.QtGui" --hidden-import "PySide6.QtWidgets" --hidden-import "PySide6.QtUiTools" --hidden-import "bs4" --hidden-import "requests" d2rcheck.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed! See errors above.
    pause
    exit /b 1
)

echo.
echo [4/4] Verifying build...
if exist "dist\D2R_Equipment_Checker.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your executable is at:
    echo   %CD%\dist\D2R_Equipment_Checker.exe
    echo.
    explorer dist
) else (
    echo.
    echo ERROR: Exe not found after build!
    echo Check the output above for errors.
)

echo.
pause
