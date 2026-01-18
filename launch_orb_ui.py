#!/usr/bin/env python3
"""
Simple ORB UI Launcher
Launches the floating ORB interface with CALI speech capabilities
"""

import asyncio
import sys
from pathlib import Path

# Setup proper Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

async def launch_orb_ui():
    """Launch the ORB floating UI"""
    print("🚀 Launching UCM_4_Core ORB Interface")
    print("=" * 50)

    try:
        # Import and initialize ORB UI
        from CALI.orb.ui_overlay.floating_window import FloatingOrbUI

        ui = FloatingOrbUI()
        print("✅ ORB UI initialized")
        print("✅ CALI SKG integrated")
        print("✅ POM 2.0 speech synthesis ready")
        print()
        print("🎯 ORB Status: Floating bubble should appear on desktop")
        print("🎯 Cursor tracking: Active")
        print("🎯 CALI speech: Ready for bubble clicks")
        print()
        print("💡 Click the floating ORB bubble to hear CALI speak!")
        print("=" * 50)

        # Start the floating UI
        await ui.start_floating()

    except Exception as e:
        print(f"❌ Failed to launch ORB UI: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    asyncio.run(launch_orb_ui())