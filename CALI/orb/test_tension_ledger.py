#!/usr/bin/env python3
"""
Test Tension Ledger - Verify disagreement detection
"""

from CALI.orb.orb_vessel import ORB_VESSEL
from CALI.orb.tension_ledger import TENSION_LEDGER

def test_tension():
    print("🧪 Testing Tension Ledger...")

    # Start ORB observation
    ORB_VESSEL.start_observation()

    # Create contradictory verdicts (should generate tension)
    ORB_VESSEL.receive_verdict(
        "Caleon_Genesis",
        {"recommendation": "ACCEPT", "confidence": 0.9},
        {"test": "tension_creation"}
    )

    ORB_VESSEL.receive_verdict(
        "Cali_X_One",
        {"recommendation": "REJECT", "confidence": 0.85},
        {"test": "tension_creation"}
    )

    # Wait for processing
    import time
    time.sleep(1)

    # Check tension summary
    summary = TENSION_LEDGER.get_summary()
    print(f"✅ Total tensions: {summary['total_tensions']}")
    print(f"✅ Unresolved: {summary['unresolved']}")
    print(f"✅ Tension level: {summary['tension_level']:.2f}")

    ORB_VESSEL.stop_observation()

    # Should have high tension (>0.7) due to contradiction
    assert summary['tension_level'] > 0.6, "Should detect high tension from contradiction"
    print("🎯 Tension Ledger: PASSED")

if __name__ == "__main__":
    test_tension()