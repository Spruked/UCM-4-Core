#!/usr/bin/env python3
"""
Minimal ORB Test - Just show the floating bubble
"""

import asyncio
import subprocess
import sys
from pathlib import Path

async def test_orb():
    print("🧪 Testing ORB System Components")
    print("=" * 40)

    # Test 1: Check if HTML renders
    html_file = Path("CALI/orb/ui_overlay/electron/index.html")
    if html_file.exists():
        print("✅ ORB HTML file exists")
    else:
        print("❌ ORB HTML file missing")
        return

    # Test 2: Check if Electron can start
    print("⏳ Testing Electron launch...")
    try:
        electron_dir = Path("CALI/orb/ui_overlay/electron")
        process = subprocess.Popen(
            ["electron", "."],
            cwd=str(electron_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        await asyncio.sleep(3)  # Wait for startup

        if process.poll() is None:
            print("✅ Electron process started")
            process.terminate()
            process.wait()
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Electron failed: {stderr.decode()}")
            return

    except Exception as e:
        print(f"❌ Electron test failed: {e}")
        return

    # Test 3: Check Python imports
    print("⏳ Testing Python imports...")
    try:
        sys.path.insert(0, '.')
        from CALI.cali_skg import CALISKGEngine
        print("✅ CALI SKG import successful")
    except ImportError as e:
        print(f"❌ CALI SKG import failed: {e}")
        return

    print("=" * 40)
    print("🎯 ORB System Test Complete")
    print("💡 The floating bubble should be visible in Chrome")
    print("💡 Electron can launch but needs Python server")
    print("💡 CALI SKG is ready for integration")

if __name__ == "__main__":
    asyncio.run(test_orb())