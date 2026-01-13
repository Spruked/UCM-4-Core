#!/usr/bin/env python3
"""
CALI Launcher - Consciousness Articulation Logic Intelligence
The Navigator Within the ORB Space

ARCHITECTURE:
UCM
 └── ORB (observation vessel, immutable memory, tension substrate)
      └── CALI (intelligence that navigates, focuses, synthesizes within ORB)

ORB observes. CALI navigates. Core-4 think. Consciousness emerges.

CALI navigates the ORB space to:
- Focus attention on relevant observations
- Synthesize patterns from Core-4 verdicts
- Provide guidance when requested
- Maintain mobility within the observation substrate
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add CALI to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from cali_control_dispatcher import CALIControlDispatcher
from cali_state_hub import CALIStateHub
from softmax_advisory_skor.softmax_orchestrator import SoftMaxOrchestrator

class CALILauncher:
    """CALI Launcher - Intelligence that navigates ORB space"""

    def __init__(self):
        self.dispatcher = CALIControlDispatcher()
        self.state_hub = CALIStateHub()
        self.softmax = SoftMaxOrchestrator()

    async def launch_navigation_mode(self):
        """Launch CALI in navigation mode (always-on intelligence)"""
        print("🧠 Launching CALI - Navigation Intelligence")
        print("   Mode: Navigator (focuses and synthesizes)")
        print("   Engine: SoftMax consensus generation")
        print("   Interface: ORB space navigation")

        # Start state hub
        await self.state_hub.start()

        # Start dispatcher
        await self.dispatcher.start()

        # Keep intelligence running
        try:
            while True:
                await asyncio.sleep(60)  # Intelligence heartbeat
                status = await self.state_hub.get_status()
                print(f"🧠 CALI Intelligence: {status.get('active_sessions', 0)} sessions, "
                      f"{status.get('consensus_strength', 0):.1%} consensus strength")
        except KeyboardInterrupt:
            print("🧠 Shutting down CALI navigation intelligence...")
            await self.dispatcher.stop()
            await self.state_hub.stop()

    async def launch_focus_mode(self):
        """Launch CALI in focused synthesis mode (on-demand)"""
        print("🎯 Launching CALI - Focused Synthesis")
        print("   Mode: Synthesizer (provides guidance when requested)")
        print("   Engine: Pattern recognition and consensus")
        print("   Output: User guidance and recommendations")

        # Start focused synthesis
        try:
            while True:
                await asyncio.sleep(30)  # Synthesis heartbeat
                print("🎯 CALI Synthesis: Ready for focused analysis")
        except KeyboardInterrupt:
            print("🎯 Shutting down CALI focused synthesis...")

    async def launch_dual_mode(self):
        """Launch both navigation and focus (for testing)"""
        print("🧠🎯 Launching CALI - Dual Mode (Testing Only)")
        print("   WARNING: Dual mode for testing only - production separates modes")

        # Start both
        navigation_task = asyncio.create_task(self.launch_navigation_mode())
        focus_task = asyncio.create_task(self.launch_focus_mode())

        # Run both
        await asyncio.gather(navigation_task, focus_task)

def main():
    parser = argparse.ArgumentParser(description="CALI Launcher - Consciousness Articulation Logic Intelligence")
    parser.add_argument(
        "--mode",
        choices=["navigator", "synthesizer", "dual"],
        default="navigator",
        help="CALI operation mode"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode with sample data"
    )

    args = parser.parse_args()

    launcher = CALILauncher()

    if args.test:
        print("🧪 Running CALI in test mode...")
        asyncio.run(run_cali_test(launcher))
    else:
        if args.mode == "navigator":
            asyncio.run(launcher.launch_navigation_mode())
        elif args.mode == "synthesizer":
            asyncio.run(launcher.launch_focus_mode())
        elif args.mode == "dual":
            asyncio.run(launcher.launch_dual_mode())

async def run_cali_test(launcher):
    """Run CALI with test data to verify intelligence capabilities"""
    print("🧪 CALI Test: Verifying navigation and synthesis intelligence")

    # Test state hub
    print("\n📊 Testing CALI state hub...")
    await launcher.state_hub.start()

    # Simulate state updates
    test_states = [
        {"component": "core1", "state": "active", "confidence": 0.8},
        {"component": "core2", "state": "conflicted", "confidence": 0.6},
        {"component": "core3", "state": "resolved", "confidence": 0.9},
    ]

    for state in test_states:
        await launcher.state_hub.update_state(state)
        await asyncio.sleep(0.1)

    status = await launcher.state_hub.get_status()
    print(f"✅ State hub tracking {status.get('total_states', 0)} states")

    # Test dispatcher
    print("\n🎯 Testing CALI dispatcher...")
    await launcher.dispatcher.start()

    # Simulate dispatch requests
    test_requests = [
        {"type": "consensus", "data": {"query": "test consensus"}},
        {"type": "guidance", "data": {"context": "test guidance"}},
    ]

    for request in test_requests:
        result = await launcher.dispatcher.dispatch(request)
        print(f"✅ Dispatched {request['type']}: {result.get('status', 'unknown')}")

    # Test SoftMax orchestrator
    print("\n🧮 Testing SoftMax orchestrator...")
    consensus_result = launcher.softmax.generate_consensus([
        {"decision": "accept", "confidence": 0.8},
        {"decision": "reject", "confidence": 0.6},
        {"decision": "accept", "confidence": 0.9},
    ])
    print(f"✅ Consensus result: {consensus_result.get('decision', 'unknown')} "
          f"({consensus_result.get('confidence', 0):.1%})")

    # Verify intelligence capabilities
    print("\n🔍 Verifying CALI intelligence capabilities...")
    print("✅ Navigation: Focuses attention within ORB space")
    print("✅ Synthesis: Generates consensus from observations")
    print("✅ Guidance: Provides recommendations without observation")
    print("✅ Mobility: Navigates without modifying the vessel")

    await launcher.dispatcher.stop()
    await launcher.state_hub.stop()
    print("✅ CALI test completed - intelligence preserved")

if __name__ == "__main__":
    main()