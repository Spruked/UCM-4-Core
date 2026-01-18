#!/usr/bin/env python3
"""
Simple ORB Launcher - Python + Electron
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

async def launch_orb():
    print("🚀 Starting UCM_4_Core ORB System")
    print("=" * 50)

    # Start Python ORB server
    print("🐍 Launching Python ORB server with CALI SKG integration...")
    python_cmd = [
        sys.executable, "-c",
        """
import asyncio
import sys
import os
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), 'CALI'))
from CALI.orb.ui_overlay.floating_window import FloatingOrbUI

async def run_orb():
    ui = FloatingOrbUI()
    print('Enhanced CALI ORB UI server started on port 8766')
    print('Features: SKG integration, voice synthesis, dynamic status updates')
    await ui.start_floating()

asyncio.run(run_orb())
"""
    ]

    python_process = subprocess.Popen(python_cmd, cwd=str(PROJECT_ROOT))

    # Wait for server to start
    print("⏳ Waiting for Python server...")
    await asyncio.sleep(3)

    # Start Electron UI
    print("⚛️ Launching Electron floating UI...")
    electron_dir = PROJECT_ROOT / "CALI" / "orb" / "ui_overlay" / "electron"
    electron_process = subprocess.Popen(["npx", "electron", "."], cwd=str(electron_dir))

    print("✅ Enhanced CALI ORB System launched!")
    print("🎯 Features:")
    print("  • CALI SKG integration with immutable personality")
    print("  • Elegant crystalline floating UI with dynamic themes")
    print("  • Voice synthesis via POM 2.0 (elegant female voice)")
    print("  • Real-time status updates (Observing → Converging → Ready)")
    print("  • Cursor tracking and application awareness")
    print("🎯 Look for elegant floating bubble on desktop")
    print("🎯 Click bubble to hear CALI speak and see status changes")
    print("=" * 60)

    # Monitor
    try:
        while True:
            await asyncio.sleep(5)
            print("✅ ORB running (Python + Electron)")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        python_process.terminate()
        electron_process.terminate()

if __name__ == "__main__":
    asyncio.run(launch_orb())