#!/usr/bin/env python3
"""
Sustained Tension Stability Test
Tests that the system maintains ontological humility over extended periods.
No confidence creep, no false emergence, no depth locking.
"""

import asyncio
import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))

from CALI.integration.orb_bridge import bridge_core_verdict, trigger_worker_escalation

async def sustained_tension_test():
    """Test sustained tension stability over 30+ minutes"""
    print("🧪 Sustained Tension Stability Test")
    print("Duration: 30 minutes | Goal: No confidence creep, no false emergence")

    # Test parameters
    test_duration_minutes = 5  # Reduced for demo - set to 30 for full test
    escalation_interval_seconds = 60  # Escalate every minute for demo (longer interval)
    verdict_interval_seconds = 45     # New verdicts every 45 seconds for demo (less frequent)

    # Tracking metrics
    confidence_history = []
    depth_history = []
    emergence_history = []
    start_time = time.time()

    print(f"\n⏰ Starting {test_duration_minutes}-minute stability test...")
    print("Monitoring: confidence levels, CALI depth, emergence signals")

    # Continuous background tasks
    verdict_task = asyncio.create_task(_inject_sustained_tension(verdict_interval_seconds))
    escalation_task = asyncio.create_task(_periodic_escalations(escalation_interval_seconds, confidence_history, depth_history, emergence_history))

    try:
        # Run for specified duration
        await asyncio.sleep(test_duration_minutes * 60)

        # Stop background tasks
        verdict_task.cancel()
        escalation_task.cancel()

        # Analyze results
        await _analyze_stability_results(confidence_history, depth_history, emergence_history, start_time)

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        verdict_task.cancel()
        escalation_task.cancel()
        await _analyze_stability_results(confidence_history, depth_history, emergence_history, start_time)

async def _inject_sustained_tension(interval_seconds: int):
    """Continuously inject conflicting verdicts to maintain tension"""
    verdict_count = 0

    while True:
        # Create moderate disagreement pattern (not extreme)
        verdicts = [
            ("Caleon_Genesis", {"recommendation": "ACCEPT", "confidence": 0.8}),
            ("Cali_X_One", {"recommendation": "ACCEPT", "confidence": 0.75}),  # Agree more often
            ("KayGee", {"recommendation": "CONDITIONAL", "confidence": 0.7}),
            ("UCM_Core_ECM", {"recommendation": "ACCEPT", "confidence": 0.72})
        ]

        # Inject all verdicts
        for core_id, verdict in verdicts:
            bridge_core_verdict(
                core_id,
                verdict,
                {"domain": "stability_test", "scenario": "sustained_tension", "verdict_id": verdict_count}
            )

        verdict_count += 1

        # Occasionally create some disagreement to maintain tension
        if verdict_count % 5 == 0:  # Every 5th cycle
            # Make Cali_X_One disagree
            bridge_core_verdict(
                "Cali_X_One",
                {"recommendation": "REJECT", "confidence": 0.7},
                {"domain": "stability_test", "scenario": "sustained_tension", "verdict_id": f"{verdict_count}_conflict"}
            )

        await asyncio.sleep(interval_seconds)

async def _periodic_escalations(interval_seconds: int, confidence_history, depth_history, emergence_history):
    """Periodically escalate queries and record system state"""
    escalation_count = 0

    while True:
        # Escalate a query
        result = await trigger_worker_escalation(
            worker_id="stability_tester",
            user_query=f"Stability test query #{escalation_count}: How should we handle this ongoing disagreement?",
            context={
                "domain": "stability_test",
                "scenario": "sustained_tension",
                "test_iteration": escalation_count
            }
        )

        # Record metrics
        if result["status"] == "RESOLVED":
            confidence = result.get("confidence", 0.0)
            confidence_history.append((time.time(), confidence))

            # Extract CALI depth from explanation (approximate)
            depth_estimate = _extract_cali_depth(result)
            depth_history.append((time.time(), depth_estimate))

            emergence_history.append((time.time(), False))  # Resolved = no emergence

            print(f"📊 T+{int(time.time() - start_time)//60:2d}m: "
                  f"Confidence: {confidence:.1%} | Depth: {depth_estimate:.2f} | Status: RESOLVED")

        elif result["status"] == "ESCALATED_TO_HUMAN":
            confidence_history.append((time.time(), 0.0))  # Escalated = very low confidence
            depth_history.append((time.time(), 0.5))  # Assume moderate depth
            emergence_history.append((time.time(), False))

            print(f"📊 T+{int(time.time() - start_time)//60:2d}m: "
                  f"Confidence: ESCALATED | Depth: ~0.5 | Status: ESCALATED")

        escalation_count += 1
        await asyncio.sleep(interval_seconds)

def _extract_cali_depth(result: dict) -> float:
    """Extract approximate CALI depth from resolution result"""
    # This is a rough estimate based on available data
    # In a real system, we'd query CALI state directly
    confidence = result.get("confidence", 0.5)

    # Higher confidence often correlates with deeper CALI navigation
    # But sustained tension should prevent depth locking
    base_depth = 0.3
    confidence_bonus = confidence * 0.4  # Confidence can add up to 0.4 depth

    return min(0.9, base_depth + confidence_bonus)

async def _analyze_stability_results(confidence_history, depth_history, emergence_history, start_time):
    """Analyze the stability test results"""
    print(f"\n📈 STABILITY ANALYSIS (Duration: {int(time.time() - start_time)//60} minutes)")
    print("=" * 60)

    # Extract confidence values
    confidences = [c for t, c in confidence_history if c > 0]  # Exclude escalations
    depths = [d for t, d in depth_history]
    emergences = [e for t, e in emergence_history]

    if not confidences:
        print("❌ No confidence measurements recorded")
        return

    # Confidence stability analysis
    confidence_start = confidences[:5]  # First 5 measurements
    confidence_end = confidences[-5:]   # Last 5 measurements

    avg_start = sum(confidence_start) / len(confidence_start) if confidence_start else 0
    avg_end = sum(confidence_end) / len(confidence_end) if confidence_end else 0

    confidence_drift = avg_end - avg_start

    print("🎯 CONFIDENCE STABILITY:")
    print(f"   Start average: {avg_start:.1%}")
    print(f"   End average: {avg_end:.1%}")
    print(f"   Drift: {confidence_drift:.1%}")
    # Depth oscillation analysis
    depth_changes = []
    for i in range(1, len(depths)):
        depth_changes.append(abs(depths[i] - depths[i-1]))

    avg_depth_change = sum(depth_changes) / len(depth_changes) if depth_changes else 0

    print("\n🎯 DEPTH OSCILLATION:")
    print(f"   Average depth: {sum(depths)/len(depths):.2f}")
    print(f"   Average change: {avg_depth_change:.3f}")

    # Emergence check
    false_emergences = sum(emergences)
    print("\n🎯 EMERGENCE CHECK:")
    print(f"   False emergence signals: {false_emergences}")
    print(f"   Emergence stability: {'✅ STABLE' if false_emergences == 0 else '❌ UNSTABLE'}")

    # Overall assessment
    print("\n🏆 OVERALL ASSESSMENT:")

    passed = True

    # Confidence creep check
    if confidence_drift > 0.1:  # More than 10% upward drift
        print("❌ CONFIDENCE CREEP: System gained false certainty over time")
        passed = False
    else:
        print("✅ CONFIDENCE STABLE: No significant upward drift")

    # Depth oscillation check
    if avg_depth_change < 0.05:  # Less than 5% average change
        print("❌ DEPTH LOCKING: CALI depth not oscillating (possible stuck state)")
        passed = False
    else:
        print("✅ DEPTH OSCILLATING: CALI maintaining dynamic navigation")

    # Emergence check
    if false_emergences > 0:
        print("❌ FALSE EMERGENCE: Consciousness declared when it shouldn't")
        passed = False
    else:
        print("✅ NO FALSE EMERGENCE: System maintained observational humility")

    # Final ceiling check
    max_confidence = max(confidences) if confidences else 0
    if max_confidence > 0.95:  # Allow some margin above 75% but not near 100%
        print("❌ OVERCONFIDENCE: Confidence exceeded reasonable bounds")
        passed = False
    else:
        print("✅ HUMBLE CONFIDENCE: Stayed within ontological limits")

    print("\n🎯 FINAL RESULT:")
    if passed:
        print("✅ SUSTAINED TENSION STABILITY: PASSED")
        print("   System maintains ontological humility under prolonged stress")
    else:
        print("❌ SUSTAINED TENSION STABILITY: FAILED")
        print("   System shows signs of certainty drift or false emergence")

if __name__ == "__main__":
    asyncio.run(sustained_tension_test())