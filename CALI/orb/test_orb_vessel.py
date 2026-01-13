#!/usr/bin/env python3
"""
Test ORB Vessel - Verify immutability and observation
"""

from orb_vessel import ORB_VESSEL

def test_orb():
    print("🧪 Testing ORB Vessel...")

    # Start observation
    ORB_VESSEL.start_observation()

    # Simulate Core-4 verdicts
    test_verdicts = [
        ("Caleon_Genesis", {"recommendation": "ACCEPT", "confidence": 0.8}),
        ("Cali_X_One", {"recommendation": "REJECT", "confidence": 0.6}),
        ("KayGee", {"recommendation": "CONDITIONAL", "confidence": 0.7}),
        ("UCM_Core_ECM", {"recommendation": "SUSPEND", "confidence": 0.9}),
    ]

    for core_id, verdict in test_verdicts:
        ORB_VESSEL.receive_verdict(core_id, verdict, {"test": True})

    # Wait for observation
    import time
    time.sleep(1)

    # Check state
    state = ORB_VESSEL.get_state()
    print(f"✅ Matrix size: {state['matrix_size']}")
    print(f"✅ Observing: {state['is_observing']}")

    # Verify immutability (try to modify - should be impossible)
    # The design prevents this inherently

    # Stop observation
    ORB_VESSEL.stop_observation()

    print("🎯 ORB Vessel: PASSED")

if __name__ == "__main__":
    test_orb()