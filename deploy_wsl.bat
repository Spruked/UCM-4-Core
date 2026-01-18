@echo off
REM UCM_4_Core/deploy_wsl.bat
REM Windows batch file to prepare for WSL deployment

echo 🚀 Preparing UCM 4 Core ORB System for WSL Deployment
echo ====================================================

REM Check if we're in the right directory
if not exist "orb_perception_integration.py" (
    echo ❌ Please run this script from the UCM_4_Core directory
    pause
    exit /b 1
)

echo ✅ Project structure verified

REM Check if requirements.txt exists
if exist "requirements.txt" (
    echo ✅ Requirements file found
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Check Kubernetes configs
if exist "k8s\" (
    echo ✅ Kubernetes configurations found
    dir k8s\*.yaml
) else (
    echo ❌ k8s directory not found
    pause
    exit /b 1
)

echo.
echo 🎯 Next steps for WSL deployment:
echo 1. Copy this folder to WSL: cp -r /mnt/c/dev/Desktop/UCM_4_Core ~
echo 2. In WSL terminal: cd UCM_4_Core
echo 3. Make script executable: chmod +x deploy_wsl.sh
echo 4. Run deployment: ./deploy_wsl.sh
echo.
echo 📋 Prerequisites in WSL:
echo - Ubuntu/Debian-based distribution
echo - sudo access
echo - Internet connection for downloads
echo.
echo ☸️  The deployment will install:
echo - Docker (if not present)
echo - k3s (lightweight Kubernetes)
echo - Build ORB Docker image
echo - Deploy all components to Kubernetes
echo.

pause