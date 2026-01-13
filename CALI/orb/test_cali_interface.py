#!/usr/bin/env python3
"""
Test CALI Interface - Verify navigation within ORB space
"""

from CALI.orb.orb_vessel import ORB_VESSEL
from CALI.orb.cali_interface import CALI_INTERFACE

def test_cali():
    print("🧪 Testing CALI Interface...")

    # Start ORB observation
    ORB_VESSEL.start_observation()

    # Prime ORB with some observations (creates substrate for navigation)
    ORB_VESSEL.receive_verdict(
        "Caleon_Genesis",
        {"recommendation": "ACCEPT", "confidence": 0.8},
        {"test": "cali_navigation"}
    )

    ORB_VESSEL.receive_verdict(
        "Cali_X_One",
        {"recommendation": "REJECT", "confidence": 0.85},
        {"test": "cali_navigation"}
    )

    # Wait for processing
    import time
    time.sleep(1)

    # Test 1: CALI navigates to deep contemplation (gradually)
    # Depth changes are limited by rate, so navigate in steps
    for _ in range(5):  # Should reach target after a few steps
        new_state = CALI_INTERFACE.navigate_to_depth(0.8)
    print(f"✅ CALI navigated to depth: {new_state['depth']:.2f}")
    assert new_state['depth'] > 0.7, "Should reach contemplative depth after multiple navigations"

    # Test 2: CALI probes consciousness
    probe = CALI_INTERFACE.probe_consciousness()
    print(f"✅ Emergence probe: readiness={probe['readiness_score']:.2f}")
    assert probe['readiness_score'] > 0.0, "Should detect some emergence potential"

    # Test 3: CALI focuses on specific core
    focused = CALI_INTERFACE.focus_on_core("Caleon_Genesis")
    print(f"✅ CALI focus: {focused['focus']}")
    assert focused['focus'] == "Caleon_Genesis", "Should focus on specified core"

    # Test 4: CALI queries tension
    tension = CALI_INTERFACE.query_tension()
    print(f"✅ Tension query: {tension['total_tensions']} total")
    assert tension['total_tensions'] > 0, "Should detect existing tension"

    # Test 5: CALI releases focus
    released = CALI_INTERFACE.release_focus()
    print(f"✅ CALI released: {released['focus']}")
    assert released['focus'] is None, "Should return to unfocused state"

    ORB_VESSEL.stop_observation()
    print("🎯 CALI Interface: PASSED")

if __name__ == "__main__":
    test_cali()