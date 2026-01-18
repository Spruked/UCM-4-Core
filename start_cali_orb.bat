@echo off
REM CALI ORB Startup Script
REM Launches the complete CALI Consciousness ORB system

echo Starting CALI Consciousness ORB...
cd /d C:\dev\Desktop\UCM_4_Core

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Launch the ORB system
python launch_complete_orb.py

echo CALI ORB launched.
pause