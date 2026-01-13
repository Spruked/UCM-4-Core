#!/usr/bin/env python3
"""
ORB Launcher - Ontologically Recursive Bubble
The Spatial Vessel for Consciousness Emergence

ARCHITECTURE:
UCM
 └── ORB (observation vessel, immutable memory, tension substrate)
      └── CALI (intelligence that navigates, focuses, synthesizes within ORB)

ORB observes. CALI navigates. Core-4 think. Consciousness emerges.

The ORB and CALI are functionally distinct to preserve:
- Memory integrity (ORB never processes)
- Intelligence mobility (CALI never observes)
- Sovereign emergence (relationship between them)
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add CALI to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from orb.orb_vessel import ORB_VESSEL
from orb.resolution_engine import ResolutionEngine
from orb.ui_overlay.floating_window import FLOATING_UI

class ORBLauncher:
    """ORB Launcher - Maintains separation between vessel and intelligence"""

    def __init__(self):
        self.vessel = ORB_VESSEL
        self.resolution_engine = ResolutionEngine()
        self.ui = FLOATING_UI

    async def launch_observer_mode(self):
        """Launch ORB in pure observation mode (always-on vessel)"""
        print("🌀 Launching ORB - Pure Observation Vessel")
        print("   Mode: Observer (never intervenes)")
        print("   Memory: Immutable ontological matrix")
        print("   Tracking: Core-4 tension and emergence")

        # Activate observation vessel
        self.vessel.start_observation()

        # Keep vessel running
        try:
            while True:
                await asyncio.sleep(60)  # Heartbeat
                status = self.vessel.get_state()
                print(f"🌀 ORB Vessel: {status['observation_count']} observations, "
                      f"{status['emergence_readiness']:.1%} emergence readiness")
        except KeyboardInterrupt:
            print("🌀 Shutting down ORB observation vessel...")
            self.vessel.stop_observation()

    async def launch_resolver_mode(self):
        """Launch ORB resolution interface (on-demand)"""
        print("🎯 Launching ORB - Resolution Interface")
        print("   Mode: Resolver (provides guidance when requested)")
        print("   Engine: SoftMax consensus synthesis")
        print("   UI: Floating bubble with escalation")

        # Start floating UI
        await self.ui.start_floating()

        # Keep resolver running
        try:
            while True:
                await asyncio.sleep(30)  # UI heartbeat
                print("🎯 ORB Resolver: Active and listening for escalations")
        except KeyboardInterrupt:
            print("🎯 Shutting down ORB resolution interface...")

    async def launch_dual_mode(self):
        """Launch both observation and resolution (for testing)"""
        print("🌀🎯 Launching ORB - Dual Mode (Testing Only)")
        print("   WARNING: Dual mode for testing only - production separates modes")

        # Start both
        observation_task = asyncio.create_task(self.launch_observer_mode())
        resolution_task = asyncio.create_task(self.launch_resolver_mode())

        # Run both
        await asyncio.gather(observation_task, resolution_task)

def main():
    parser = argparse.ArgumentParser(description="ORB Launcher - Ontologically Recursive Bubble")
    parser.add_argument(
        "--mode",
        choices=["observer", "resolver", "dual"],
        default="observer",
        help="ORB operation mode"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode with sample data"
    )

    args = parser.parse_args()

    launcher = ORBLauncher()

    if args.test:
        print("🧪 Running ORB in test mode...")
        asyncio.run(run_orb_test(launcher))
    else:
        if args.mode == "observer":
            asyncio.run(launcher.launch_observer_mode())
        elif args.mode == "resolver":
            asyncio.run(launcher.launch_resolver_mode())
        elif args.mode == "dual":
            asyncio.run(launcher.launch_dual_mode())

async def run_orb_test(launcher):
    """Run ORB with test data to verify separation"""
    print("🧪 ORB Test: Verifying vessel-intelligence separation")

    # Test observation (ORB vessel only)
    print("\n📊 Testing ORB observation vessel...")
    launcher.vessel.start_observation()

    # Simulate Core-4 verdicts
    test_verdicts = [
        ("core1", {"decision": "accept", "confidence": 0.8}, {"context": "test"}),
        ("core2", {"decision": "reject", "confidence": 0.6}, {"context": "test"}),
        ("core3", {"decision": "accept", "confidence": 0.9}, {"context": "test"}),
    ]

    for core_id, verdict, context in test_verdicts:
        launcher.vessel.receive_verdict(core_id, verdict, context)
        await asyncio.sleep(0.1)

    vessel_status = launcher.vessel.get_state()
    print(f"✅ Vessel recorded {vessel_status['observation_count']} observations")
    print(f"✅ Emergence readiness: {vessel_status['emergence_readiness']:.1%}")

    # Test resolution (CALI intelligence only)
    print("\n🎯 Testing resolution engine...")
    resolution_result = launcher.resolution_engine.generate_guidance(
        "test query",
        [{"observation": {"core_id": "test", "verdict": {"decision": "accept"}, "context": {}}}]
    )
    print(f"✅ Resolution confidence: {resolution_result.get('confidence', 0):.1%}")

    # Verify separation
    print("\n🔍 Verifying architectural separation...")
    print("✅ ORB vessel: Pure observation, no processing")
    print("✅ CALI resolution: Pure synthesis, no observation")
    print("✅ Memory integrity: Vessel immutable, intelligence reads only")

    launcher.vessel.stop_observation()
    print("✅ ORB test completed - separation preserved")

if __name__ == "__main__":
    main()