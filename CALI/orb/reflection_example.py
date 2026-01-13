#!/usr/bin/env python3
"""
Example: Starting the Reflection Loop in Main Application

This shows how to integrate the reflection loop into your main UCM_4_Core application.
"""

import sys
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from CALI.orb.orb_vessel import ORB_VESSEL
from CALI.orb.skg_engine import SKG_ENGINE
from CALI.orb.reflection.reflection_loop import reflection_loop

async def main():
    """Main application with reflection loop"""

    # Shared state for idle detection (update with real system metrics)
    system_state = {'load': 0.0}  # Start idle for demo

    print("🚀 Starting UCM_4_Core with Reflection Loop...")

    # Start reflection loop as background task
    reflection_task = asyncio.create_task(
        reflection_loop(
            shared_state=system_state,
            orb_vessel=ORB_VESSEL,
            skg_engine=SKG_ENGINE
        ),
        name="ReflectionLoop"
    )

    print("✅ Reflection loop started")
    print("System will now learn from observation patterns during idle periods")

    # Simulate some activity
    await asyncio.sleep(2)

    # Update system load (simulate becoming busy)
    system_state['load'] = 0.8
    print("📈 System load increased to 80% - reflection paused")

    await asyncio.sleep(2)

    # Update system load (simulate becoming idle again)
    system_state['load'] = 0.05
    print("📉 System load decreased to 5% - reflection may resume")

    # Let it run a bit more
    await asyncio.sleep(5)

    print("🛑 Stopping demo...")
    reflection_task.cancel()

    try:
        await reflection_task
    except asyncio.CancelledError:
        print("✅ Reflection loop stopped cleanly")

if __name__ == "__main__":
    asyncio.run(main())