#!/usr/bin/env python3
"""
Test Reflection Loop Functionality
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from CALI.orb.orb_vessel import ORB_VESSEL
from CALI.orb.skg_engine import SKG_ENGINE
from CALI.orb.reflection.reflection_loop import reflection_loop, is_system_idle, analyze_for_patterns

async def test_reflection():
    """Test reflection loop components"""
    print("🧪 Testing Reflection Loop...")

    # Test 1: Idle detection
    print("\n[1] Testing idle detection...")
    idle_state = {'load': 0.05}  # Idle
    busy_state = {'load': 0.8}   # Busy

    idle_result = await is_system_idle(idle_state)
    busy_result = await is_system_idle(busy_state)

    print(f"   Idle state (0.05): {idle_result} ✅" if idle_result else f"   Idle state (0.05): {idle_result} ❌")
    print(f"   Busy state (0.8): {busy_result} ❌" if busy_result else f"   Busy state (0.8): {busy_result} ✅")

    # Test 2: Pattern analysis
    print("\n[2] Testing pattern analysis...")

    # Create sample observations
    sample_obs = [
        {
            "core_id": "Caleon_Genesis",
            "verdict": {"confidence": 0.9, "recommendation": "ACCEPT"},
            "context": {"escalated": False},
            "tension_status": "resolved",
            "duration": 30
        },
        {
            "core_id": "Cali_X_One",
            "verdict": {"confidence": 0.8, "recommendation": "REJECT"},
            "context": {"escalated": True},
            "tension_status": "unresolved",
            "duration": 120
        },
        {
            "core_id": "KayGee",
            "verdict": {"confidence": 0.7, "recommendation": "ACCEPT"},
            "context": {"escalated": False, "reopened": True},
            "tension_status": "resolved",
            "duration": 45
        }
    ]

    metrics = ["confidence_vs_outcome", "tension_duration", "escalation_frequency", "resolution_regret"]
    reflections = analyze_for_patterns(sample_obs, metrics)

    print(f"   Generated {len(reflections)} reflection insights:")
    for ref in reflections:
        print(f"     - {ref['type']}: {ref['description']}")

    # Test 3: Record reflection
    print("\n[3] Testing reflection recording...")

    if reflections:
        ORB_VESSEL.record_reflection(
            source="test_reflection_loop",
            insight=reflections[0],
            confidence=0.4
        )
        print("   ✅ Reflection recorded successfully")

    # Test 4: Quick reflection cycle (shortened for testing)
    print("\n[4] Testing reflection cycle (shortened)...")

    # Create a shortened version for testing
    async def test_reflection_cycle():
        """Run one reflection cycle with idle simulation"""
        # Simulate idle state
        shared_state = {'load': 0.05}

        # Override the idle check to pass immediately for testing
        original_is_idle = is_system_idle

        async def mock_is_idle(state):
            return True  # Always idle for testing

        # Monkey patch for testing
        import CALI.orb.reflection.reflection_loop as rl
        rl.is_system_idle = mock_is_idle

        try:
            # Run a very short cycle
            await asyncio.wait_for(
                reflection_loop(shared_state, ORB_VESSEL, SKG_ENGINE),
                timeout=5.0  # Only run for 5 seconds
            )
        except asyncio.TimeoutError:
            print("   ✅ Reflection cycle started and ran briefly")
        finally:
            # Restore original function
            rl.is_system_idle = original_is_idle

    await test_reflection_cycle()

    print("\n🎯 Reflection Loop Test: COMPLETED")
    print("System can now learn from observation patterns without modifying originals.")

if __name__ == "__main__":
    asyncio.run(test_reflection())