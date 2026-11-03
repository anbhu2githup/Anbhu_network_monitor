
@echo off
title Network Fixer - EXE Builder

echo ==========================================
echo       NETWORK FIXER BUILD PROCESS
echo ==========================================

python -m pip install --upgrade pyinstaller

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller installation failed.
    pause
    exit /b 1
)

python -m py_compile network_fixer.py

if errorlevel 1 (
    echo.
    echo ERROR: Python syntax check failed.
    pause
    exit /b 1
)

python -m PyInstaller --clean --onefile --uac-admin --name NetworkFixer network_fixer.py

if errorlevel 1 (
    echo.
    echo ERROR: EXE build failed.
) else (
    echo.
    echo BUILD SUCCESSFUL!
    echo EXE location: dist\NetworkFixer.exe
)

pause
