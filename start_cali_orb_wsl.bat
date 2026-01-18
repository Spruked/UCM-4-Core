@echo off
REM CALI ORB WSL2 Launcher
REM Launches the CALI system in WSL2 environment

echo Starting CALI Consciousness ORB in WSL2...
echo ==========================================

REM Check if WSL is available
wsl --list >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ WSL not found. Please install WSL2 first.
    echo Visit: https://docs.microsoft.com/en-us/windows/wsl/install
    pause
    exit /b 1
)

echo ✅ WSL detected

REM Launch WSL and run the ORB system
wsl bash -c "cd /mnt/c/dev/Desktop/UCM_4_Core && source .venv/bin/activate && python launch_complete_orb.py"

echo CALI ORB launched in WSL2.
pause